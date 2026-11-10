from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Driver


class DriverSerializer(serializers.ModelSerializer):
    driver_email = serializers.EmailField(max_length=127)
    driver_password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Driver
        fields = ("id", "driver_name", "driver_cpf", "driver_cnh", "driver_email",
                  "driver_password", "driver_account_created_at")
        read_only_fields = ("id", "driver_account_created_at")

    def create(self, validated_data):
        password = validated_data.pop("driver_password")
        return Driver.objects.create(driver_password_hash=make_password(password), **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("driver_password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.driver_password_hash = make_password(password)
        instance.save()
        return instance


class CreateDriverSerializer(DriverSerializer):
    driver_password = serializers.CharField(write_only=True, required=True, allow_blank=False)
