from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.client import Client


class ListClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'id',
            'clientName',
            'clientAdress',
            'clientCPF',
            'clientEmail',
            'clientAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'clientAccountCreatedAt',
        )


class ClientSerializer(serializers.ModelSerializer):
    clientPassword = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Client
        fields = (
            'id',
            'clientName',
            'clientAdress',
            'clientCPF',
            'clientEmail',
            'clientPassword',
            'clientAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'clientAccountCreatedAt',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('clientPassword', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.clientPasswordHash = make_password(password)

        instance.save()

        return instance


class CreateClientSerializer(serializers.ModelSerializer):
    clientPassword = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Client
        fields = (
            'id',
            'clientName',
            'clientAdress',
            'clientCPF',
            'clientEmail',
            'clientPassword',
            'clientAccountCreatedAt',
        )
        read_only_fields = (
            'id',
            'clientAccountCreatedAt',
        )

    def create(self, validated_data):
        password = validated_data.pop('clientPassword')

        validated_data['clientPasswordHash'] = make_password(password)

        return Client.objects.create(**validated_data)