from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models.client import Client


class ListClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'id',
            'client_name',
            'client_adress',
            'client_cpf',
            'client_email',
            'client_account_created_at',
        )
        read_only_fields = (
            'id',
            'client_account_created_at',
        )


class ClientSerializer(serializers.ModelSerializer):
    client_password = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Client
        fields = (
            'id',
            'client_name',
            'client_adress',
            'client_cpf',
            'client_email',
            'client_password',
            'client_account_created_at',
        )
        read_only_fields = (
            'id',
            'client_account_created_at',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('client_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.client_password_hash = make_password(password)

        instance.save()

        return instance


class CreateClientSerializer(serializers.ModelSerializer):
    client_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = Client
        fields = (
            'id',
            'client_name',
            'client_adress',
            'client_cpf',
            'client_email',
            'client_password',
            'client_account_created_at',
        )
        read_only_fields = (
            'id',
            'client_account_created_at',
        )

    def create(self, validated_data):
        password = validated_data.pop('client_password')

        validated_data['client_password_hash'] = make_password(password)

        return Client.objects.create(**validated_data)
