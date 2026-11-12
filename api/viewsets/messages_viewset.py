from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from firebase_admin.exceptions import FirebaseError
from google.api_core.exceptions import GoogleAPICallError
from django.db.models import Q

from api.auth.permissions import TokenUserPermission, get_payload
from api.models import Client, Company, Device
from api.serializers.messages_serializer import (
    ChatListQuerySerializer,
    CreateChatSerializer,
    MessagesQuerySerializer,
    SendMessageSerializer,
)
from api.viewsets.base import ApiModelViewSet
from api.webservices.chat_service.chat_service import (
    ChatAccessError,
    ChatNotFoundError,
    ChatValidationError,
    create_chat,
    get_chat,
    get_messages,
    list_chats,
    mark_messages_read,
)
from api.webservices.firebase.firebase import (
    FirebaseConfigurationError,
    generate_firebase_token,
)
from api.webservices.messages.messages import send_message


ACCOUNT_MODELS = {"client": Client, "company": Company}


def account_exists(user_type, user_id):
    model = ACCOUNT_MODELS.get(user_type)
    return model is not None and model.objects.filter(pk=user_id).exists()


def api_error(code, message, response_status):
    return Response(
        {"error": {"code": code, "message": message}},
        status=response_status,
    )


class MessageViewSet(ApiModelViewSet):
    permission_classes = [TokenUserPermission]
    authentication_classes = [JWTStatelessUserAuthentication]
    queryset = []
    http_method_names = ["get", "post", "head", "options"]

    def can_perform_action(self, request, payload):
        return (
            payload.get("user_type") in ("client", "company")
            and payload.get("user_id") is not None
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreateChatSerializer
        if self.action == "messages":
            return SendMessageSerializer if self.request.method == "POST" else MessagesQuerySerializer
        if self.action == "list":
            return ChatListQuerySerializer
        return SendMessageSerializer

    def _identity(self, request):
        payload = get_payload(request) or {}
        user_type = payload.get("user_type")
        user_id = str(payload.get("user_id"))
        return user_type, user_id, f"{user_type}_{user_id}"

    def _service_error(self, error):
        if isinstance(error, ChatNotFoundError):
            return api_error("CHAT_NOT_FOUND", str(error), status.HTTP_404_NOT_FOUND)
        if isinstance(error, ChatAccessError):
            return api_error("FORBIDDEN", str(error), status.HTTP_403_FORBIDDEN)
        if isinstance(error, (ChatValidationError, ValueError)):
            return api_error("INVALID_CHAT_REQUEST", str(error), status.HTTP_400_BAD_REQUEST)
        if isinstance(error, (FirebaseConfigurationError, FirebaseError, GoogleAPICallError, OSError)):
            return api_error(
                "FIRESTORE_UNAVAILABLE",
                "O serviço de conversas está indisponível.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        raise error

    def list(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user_type, user_id, user_uid = self._identity(request)
        try:
            result = list_chats(
                user_uid,
                user_type,
                limit=serializer.validated_data["limit"],
                cursor=serializer.validated_data.get("cursor"),
            )
        except Exception as error:
            return self._service_error(error)
        return Response({"data": result}, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_type, user_id, user_uid = self._identity(request)
        company_id = serializer.validated_data["company_id"]
        client_id = serializer.validated_data["client_id"]

        if (user_type == "client" and user_id != str(client_id)) or (
            user_type == "company" and user_id != str(company_id)
        ):
            return api_error(
                "FORBIDDEN",
                "Você não pode criar uma conversa em nome de outro participante.",
                status.HTTP_403_FORBIDDEN,
            )
        if not account_exists("company", company_id) or not account_exists("client", client_id):
            return api_error(
                "PARTICIPANT_NOT_FOUND",
                "Cliente ou empresa não encontrado.",
                status.HTTP_404_NOT_FOUND,
            )
        devices = Device.objects.filter(client_id=client_id)
        if user_type == "company":
            has_related_device = devices.filter(
                Q(current_company_id=company_id) | Q(current_company__isnull=True)
            ).exists()
        else:
            has_related_device = devices.filter(
                current_company_id=company_id,
                offered_value__isnull=False,
            ).exists()
        if not has_related_device:
            return api_error(
                "NO_CHAT_CONTEXT",
                "A conversa precisa estar relacionada a um equipamento disponível ou ofertado.",
                status.HTTP_403_FORBIDDEN,
            )

        try:
            chat = create_chat(company_id, client_id, user_uid)
        except Exception as error:
            return self._service_error(error)
        return Response({"data": chat}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        _, _, user_uid = self._identity(request)
        try:
            chat = get_chat(pk, user_uid)
        except Exception as error:
            return self._service_error(error)
        return Response({"data": chat}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        _, _, user_uid = self._identity(request)
        if request.method == "GET":
            serializer = self.get_serializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            try:
                result = get_messages(
                    pk,
                    user_uid,
                    limit=serializer.validated_data["limit"],
                    cursor=serializer.validated_data.get("cursor"),
                )
            except Exception as error:
                return self._service_error(error)
            return Response({"data": result}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            message = send_message(pk, user_uid, serializer.validated_data["text"])
        except Exception as error:
            return self._service_error(error)
        return Response({"data": message}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        _, _, user_uid = self._identity(request)
        try:
            result = mark_messages_read(pk, user_uid)
        except Exception as error:
            return self._service_error(error)
        return Response({"data": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="firebase-token")
    def firebase_token(self, request):
        user_type, user_id, _ = self._identity(request)
        if not account_exists(user_type, user_id):
            return api_error(
                "ACCOUNT_NOT_FOUND",
                "Conta não encontrada.",
                status.HTTP_404_NOT_FOUND,
            )
        try:
            token = generate_firebase_token(user_id, user_type)
        except Exception as error:
            return self._service_error(error)
        return Response({"data": {"customToken": token}}, status=status.HTTP_200_OK)
