from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Client


class ClientSerializer(serializers.ModelSerializer):
    client_email = serializers.EmailField(max_length=127)
    client_password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Client
        fields = ("id", "client_name", "client_adress", "client_cpf", "client_email",
                  "client_password", "client_account_created_at", "money_rewarded")
        read_only_fields = ("id", "client_account_created_at", "money_rewarded")

    def create(self, validated_data):
        password = validated_data.pop("client_password")
        return Client.objects.create(client_password=make_password(password), **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("client_password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.client_password = make_password(password)
        instance.save()
        return instance


class CreateClientSerializer(ClientSerializer):
    client_password = serializers.CharField(write_only=True, required=True, allow_blank=False)
