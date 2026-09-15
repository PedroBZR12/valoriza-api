from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        max_length=127,
        required=True
    )
    password = serializers.CharField(
        write_only=True,
        required=True
    )