from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import urlparse

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.test import RequestFactory, SimpleTestCase, override_settings
from PIL import Image

from api.models import Device, Ride
from api.serializers.device_serializer import DeviceSerializer
from api.serializers.logistics_serializer import RideSerializer


class DeviceSerializerImageTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().post("/", HTTP_HOST="valoriza.test")
        self.data = {
            "device_category": Device.Category.GREEN,
            "device_condition": Device.Condition.USED,
            "device_model": "Notebook",
            "device_description": "Tela danificada",
        }

    def image_upload(self):
        image_buffer = BytesIO()
        Image.new("RGB", (1, 1), color="red").save(image_buffer, format="PNG")
        return SimpleUploadedFile(
            "device.png", image_buffer.getvalue(), content_type="image/png"
        )

    def test_device_image_is_required_when_creating(self):
        serializer = DeviceSerializer(data=self.data, context={"request": self.request})

        self.assertFalse(serializer.is_valid())
        self.assertIn("device_image_file", serializer.errors)

    def test_uploaded_image_is_saved_and_returned_as_absolute_url(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                serializer = DeviceSerializer(
                    data={**self.data, "device_image_file": self.image_upload()},
                    context={"request": self.request},
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)

                with patch.object(
                    Device.objects, "create", side_effect=lambda **fields: Device(**fields)
                ) as create_device:
                    device = serializer.create(serializer.validated_data)

                image_url = create_device.call_args.kwargs["device_image"]
                parsed_url = urlparse(image_url)
                self.assertEqual(parsed_url.scheme, "http")
                self.assertEqual(parsed_url.netloc, "valoriza.test")
                self.assertTrue(parsed_url.path.startswith("/media/devices/"))
                self.assertTrue(default_storage.exists(parsed_url.path.removeprefix("/media/")))
                self.assertEqual(DeviceSerializer(device).data["device_image"], image_url)

    def test_ride_response_includes_its_device_image_url(self):
        image_url = "https://images.example/device.png"
        device = Device(
            device_category=Device.Category.GREEN,
            device_condition=Device.Condition.USED,
            device_model="Notebook",
            device_description="Tela danificada",
            device_image=image_url,
        )

        self.assertEqual(RideSerializer(Ride(device=device)).data["device_image"], image_url)

    def test_existing_device_without_image_can_be_updated(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                device = Device(
                    device_category=Device.Category.GREEN,
                    device_condition=Device.Condition.USED,
                    device_model="Notebook",
                    device_description="Tela danificada",
                )
                serializer = DeviceSerializer(
                    device,
                    data={"device_image_file": self.image_upload()},
                    partial=True,
                    context={"request": self.request},
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)

                with patch.object(Device, "save"):
                    updated_device = serializer.save()

                self.assertTrue(updated_device.device_image.startswith("http://valoriza.test/media/"))
