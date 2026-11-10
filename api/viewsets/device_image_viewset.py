from rest_framework.exceptions import PermissionDenied

from api.auth.permissions import TokenUserPermission
from api.models import DeviceImage
from api.serializers.device_image_serializer import DeviceImageSerializer
from api.viewsets.base import ApiModelViewSet


class DeviceImageViewSet(ApiModelViewSet):
    serializer_class = DeviceImageSerializer
    permission_classes = (TokenUserPermission,)
    filterset_fields = ("device", "image_type")
    ordering_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)

    def can_perform_action(self, request, payload):
        return payload.get("user_type") in ("client", "company", "admin")

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        role, user_id = payload.get("user_type"), payload.get("user_id")
        queryset = DeviceImage.objects.select_related("device", "device__client", "device__current_company")
        if role == "client":
            queryset = queryset.filter(device__client_id=user_id)
        elif role == "company":
            queryset = queryset.filter(device__current_company_id=user_id)
        return queryset.order_by("-uploaded_at")

    def user_can_access_object(self, request, obj, payload):
        role, user_id = payload.get("user_type"), payload.get("user_id")
        if role == "admin" or request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if self.action == "create":
            return ((role == "client" and obj.device.client_id == user_id) or
                    (role == "company" and obj.device.current_company_id == user_id))
        return ((role == "client" and obj.device.client_id == user_id) or
                (role == "company" and obj.device.current_company_id == user_id))

    def perform_create(self, serializer):
        payload = self.request.auth.payload
        device = serializer.validated_data["device"]
        owns_device = ((payload.get("user_type") == "client" and device.client_id == payload.get("user_id")) or
                       (payload.get("user_type") == "company" and device.current_company_id == payload.get("user_id")))
        if payload.get("user_type") != "admin" and not owns_device:
            raise PermissionDenied("A imagem deve pertencer a um dispositivo acessível à conta autenticada.")
        serializer.save()

