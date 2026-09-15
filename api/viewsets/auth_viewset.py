from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from api.auth.backends import authenticate_user
from api.auth.tokens import generate_tokens
from api.serializers.auth_serializer import LoginSerializer
from api.serializers.client_serializer import CreateClientSerializer
from api.serializers.company_serializer import CreateCompanySerializer
from api.serializers.driver_serializer import CreateDriverSerializer


class AuthViewSet(viewsets.GenericViewSet):
    parser_classes = (JSONParser, MultiPartParser, FormParser,)

    serializers = {
        'login': LoginSerializer,
        'create': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action) or self.serializers.get(None)

    @action(
        detail=False,
        methods=['post'],
        url_path='login'
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'error': True,
                    'message': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        user_data = authenticate_user(identifier, password)

        if not user_data:
            return Response(
                {
                    'error': True,
                    'message': 'Credenciais inválidas.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = generate_tokens(user_data)

        return Response(
            {
                'error': False,
                'message': 'Login realizado com sucesso.',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': user_data['user_id'],
                    'name': user_data['user_name'],
                    'type': user_data['user_type'],
                }
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='register'
    )
    def register(self, request):
        account_type = request.data.get('account_type')

        if not account_type:
            return Response(
                {
                    'error': True,
                    'message': 'O campo account_type é obrigatório.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_classes = {
            'client': CreateClientSerializer,
            'company': CreateCompanySerializer,
            'driver': CreateDriverSerializer,
        }

        serializer_class = serializer_classes.get(account_type)

        if not serializer_class:
            return Response(
                {
                    'error': True,
                    'message': (
                        'account_type inválido. '
                        'Use client, company ou driver.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = serializer_class(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    'error': True,
                    'message': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = serializer.save()

        return Response(
            {
                'error': False,
                'message': 'Conta criada com sucesso.',
                'data': serializer_class(instance).data,
            },
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='logout'
    )
    def logout(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {
                    'error': True,
                    'message': 'O refresh token é obrigatório.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {
                    'error': True,
                    'message': 'Refresh token inválido ou já revogado.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'error': False,
                'message': 'Logout realizado com sucesso.'
            },
            status=status.HTTP_200_OK
        )