from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage
from PIL import Image
from rest_framework import serializers
from api.models import Device

IMAGE_EXTENSIONS = {
    "GIF": ".gif",
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


class DeviceSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    device_image_file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ['id', 'client', 'created_at', 'device_status', 'offered_at',
                            'current_company', 'device_image']

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is None:
            fields["device_image_file"].required = True
        request = self.context.get("request")
        token = getattr(request, "auth", None) if request else None
        payload = getattr(token, "payload", {}) if token else {}
        role = payload.get("user_type")

        if role == "client":
            fields["offered_value"].read_only = True
        elif role == "company":
            for name in ("expected_offer", "device_category", "device_condition",
                         "device_model", "device_description"):
                fields[name].read_only = True
            fields["device_image_file"].read_only = True
        return fields

    def validate_device_image_file(self, image):
        if image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("A imagem deve ter no máximo 5 MB.")
        image.seek(0)
        try:
            with Image.open(image) as decoded_image:
                image_format = decoded_image.format
        except (OSError, ValueError) as error:
            raise serializers.ValidationError("Envie uma imagem válida.") from error
        image.seek(0)
        extension = IMAGE_EXTENSIONS.get(image_format or "")
        if extension is None:
            raise serializers.ValidationError("Envie uma imagem JPEG, PNG, WebP ou GIF.")
        image.name = f"device{extension}"
        return image

    def create(self, validated_data):
        image = validated_data.pop("device_image_file")
        validated_data["device_image"] = self.store_device_image(image)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.pop("device_image_file", None)
        if image is not None:
            if instance.device_image:
                raise serializers.ValidationError({
                    "device_image_file": "Este dispositivo já possui uma imagem."
                })
            validated_data["device_image"] = self.store_device_image(image)
        return super().update(instance, validated_data)

    def store_device_image(self, image):
        extension = Path(image.name).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            extension = ".jpg"
        image_path = default_storage.save(f"devices/{uuid4().hex}{extension}", image)
        request = self.context["request"]
        return request.build_absolute_uri(
            default_storage.url(image_path)
        )

    def validate_offered_value(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O valor ofertado deve ser maior que zero.")
        if self.instance and self.instance.offered_value is not None and value != self.instance.offered_value:
            raise serializers.ValidationError("A oferta não pode ser alterada depois de proposta.")
        return value

    def validate_expected_offer(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O valor esperado deve ser maior que zero.")
        return value

    def validate_device_condition(self, value):
        if self.instance and value != self.instance.device_condition:
            raise serializers.ValidationError("A condição do dispositivo não pode ser alterada.")
        return value
