from rest_framework import serializers
from api.models import Device

class DeviceSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

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

    def validate_current_company(self, value):
        request = self.context.get("request")
        token = getattr(request, "auth", None) if request else None
        payload = getattr(token, "payload", {}) if token else {}
        if payload.get("user_type") == "company" and value and value.pk != payload.get("user_id"):
            raise serializers.ValidationError("Uma empresa só pode se associar ao próprio cadastro.")
        if payload.get("user_type") == "client" and value:
            raise serializers.ValidationError("O cliente não pode atribuir a empresa do dispositivo.")
        return value
