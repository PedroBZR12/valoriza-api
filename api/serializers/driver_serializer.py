from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.deliverydriver import Driver


class ListDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = (
            'id',
            'driver_name',
            'driver_cpf',
            'driver_cnh',
            'driver_email',
            'driver_account_created_at',
        )
        read_only_fields = (
            'id',
            'driver_account_created_at',
        )


class DriverSerializer(serializers.ModelSerializer):
    driver_password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Driver
        fields = (
            'id',
            'driver_name',
            'driver_cpf',
            'driver_cnh',
            'driver_email',
            'driver_password',
            'driver_account_created_at',
        )
        read_only_fields = (
            'id',
            'driver_account_created_at',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('driver_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.driver_password_hash = make_password(password)

        instance.save()

        return instance


class CreateDriverSerializer(serializers.ModelSerializer):
    driver_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Driver
        fields = (
            'id',
            'driver_name',
            'driver_cpf',
            'driver_cnh',
            'driver_email',
            'driver_password',
            'driver_account_created_at',
        )
        read_only_fields = (
            'id',
            'driver_account_created_at',
        )

    def create(self, validated_data):
        password = validated_data.pop('driver_password')

        validated_data['driver_password_hash'] = make_password(password)

        return Driver.objects.create(**validated_data)
