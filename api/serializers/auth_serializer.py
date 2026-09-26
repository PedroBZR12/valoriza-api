from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        max_length=127,
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        trim_whitespace=False
    )

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier:
            raise serializers.ValidationError({
                'identifier': 'O e-mail, CPF ou identificador é obrigatório.'
            })

        if not password:
            raise serializers.ValidationError({
                'password': 'A senha é obrigatória.'
            })

        return attrs