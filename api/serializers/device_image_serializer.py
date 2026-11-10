from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from api.models.deviceImage import DeviceImage

class DeviceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceImage
        fields = ('id', 'device', 'image_url', 'image_type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')

    def validate_device(self, device):
        request = self.context.get("request")
        token = getattr(request, "auth", None) if request else None
        payload = getattr(token, "payload", {}) if token else {}
        role, user_id = payload.get("user_type"), payload.get("user_id")
        if role == "client" and device.client_id != user_id:
            raise PermissionDenied("O dispositivo pertence a outro cliente.")
        if role == "company" and device.current_company_id != user_id:
            raise PermissionDenied("O dispositivo não está associado a esta empresa.")
        return device
