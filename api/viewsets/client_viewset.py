from api.auth.permissions import AccountResourcePermission
from api.models import Client
from api.serializers.client_serializer import ClientSerializer, CreateClientSerializer
from api.viewsets.base import ApiModelViewSet


class ClientViewSet(ApiModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = (AccountResourcePermission,)
    account_role = "client"

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        if payload.get("user_type") == "admin":
            return Client.objects.all().order_by("id")
        return Client.objects.filter(pk=payload.get("user_id"))

    def get_serializer_class(self):
        return CreateClientSerializer if self.action == "create" else ClientSerializer
