from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from api.models import Client, Company, Driver


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


class AccountTokenRefreshSerializer(TokenRefreshSerializer):
    account_models = {
        "client": Client,
        "company": Company,
        "driver": Driver,
    }

    def validate(self, attrs):
        try:
            refresh = self.token_class(attrs["refresh"])
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc

        user_type = refresh.payload.get("user_type")
        user_id = refresh.payload.get("user_id")
        account_model = self.account_models.get(user_type)
        if (
            account_model is None
            or type(user_id) is not int
            or not account_model.objects.filter(pk=user_id).exists()
        ):
            raise InvalidToken("A conta associada ao token não existe.")

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                refresh.blacklist()

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()
            data["refresh"] = str(refresh)

        return data