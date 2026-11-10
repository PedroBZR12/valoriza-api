from api.auth.permissions import AccountResourcePermission
from api.models import Driver
from api.serializers.driver_serializer import DriverSerializer, CreateDriverSerializer
from api.viewsets.base import ApiModelViewSet


class DriverViewSet(ApiModelViewSet):
    serializer_class = DriverSerializer
    permission_classes = (AccountResourcePermission,)
    account_role = "driver"

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        if payload.get("user_type") == "admin":
            return Driver.objects.all().order_by("id")
        return Driver.objects.filter(pk=payload.get("user_id"))

    def get_serializer_class(self):
        return CreateDriverSerializer if self.action == "create" else DriverSerializer
