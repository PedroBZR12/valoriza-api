from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.deliverydriver import Driver


class ListDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = (
            'id',
            'driverName',
            'driverCPF',
            'driverCNH',
            'driverEmail',
            'driverAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'driverAccountCreatedAt',
        )


class DriverSerializer(serializers.ModelSerializer):
    driverPassword = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Driver
        fields = (
            'id',
            'driverName',
            'driverCPF',
            'driverCNH',
            'driverEmail',
            'driverPassword',
            'driverAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'driverAccountCreatedAt',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('driverPassword', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.driverPasswordHash = make_password(password)

        instance.save()

        return instance


class CreateDriverSerializer(serializers.ModelSerializer):
    driverPassword = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Driver
        fields = (
            'id',
            'driverName',
            'driverCPF',
            'driverCNH',
            'driverEmail',
            'driverPassword',
            'driverAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'driverAccountCreatedAt',
        )

    def create(self, validated_data):
        password = validated_data.pop('driverPassword')

        validated_data['driverPasswordHash'] = make_password(password)

        return Driver.objects.create(**validated_data)