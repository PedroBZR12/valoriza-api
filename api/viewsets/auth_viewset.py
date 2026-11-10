from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from api.auth.backends import authenticate_user
from api.auth.tokens import generate_tokens
from api.serializers.auth_serializer import LoginSerializer
from api.serializers.client_serializer import CreateClientSerializer
from api.serializers.company_serializer import CreateCompanySerializer
from api.serializers.driver_serializer import CreateDriverSerializer


class AuthViewSet(viewsets.GenericViewSet):
    parser_classes = (JSONParser, MultiPartParser, FormParser,)
    permission_classes = [AllowAny]

    serializers = {
        'login': LoginSerializer,
        'create': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action) or self.serializers.get(None)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        user_data = authenticate_user(identifier, password)

        if not user_data:
            return Response({'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Credenciais inválidas.'}}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = generate_tokens(user_data)

        return Response(
            {'data': {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': user_data['user_id'],
                    'name': user_data['user_name'],
                    'type': user_data['user_type'],
                }
            }}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        account_type = request.data.get('account_type')

        if not isinstance(account_type, str) or not account_type:
            raise ValidationError({'account_type': 'Este campo é obrigatório.'})

        serializer_classes = {
            'client': CreateClientSerializer,
            'company': CreateCompanySerializer,
            'driver': CreateDriverSerializer,
        }

        serializer_class = serializer_classes.get(account_type)

        if not serializer_class:
            raise ValidationError({'account_type': 'Use client, company ou driver.'})

        serializer = serializer_class(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response({'data': serializer_class(instance).data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            raise ValidationError({'refresh': 'Este campo é obrigatório.'})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError({'refresh': 'Token inválido ou já revogado.'})

        return Response({'data': {'message': 'Logout realizado com sucesso.'}}, status=status.HTTP_200_OK)
