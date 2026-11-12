from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db.models import Q

from api.auth.permissions import TokenUserPermission
from api.models import Device
from api.serializers.device_serializer import DeviceSerializer
from api.viewsets.base import ApiModelViewSet


class DeviceViewSet(ApiModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = (TokenUserPermission,)
    filterset_fields = {
        "device_category": ("exact",),
        "device_condition": ("exact",),
        "device_status": ("exact",),
        "client": ("exact",),
        "current_company": ("exact", "isnull"),
    }
    ordering_fields = ("created_at", "offered_value", "device_model")
    ordering = ("-created_at",)

    def can_perform_action(self, request, payload):
        role = payload.get("user_type")
        if role == "admin":
            return True
        if self.action in ("create", "destroy", "respond"):
            return role == "client"
        if self.action in ("update", "partial_update"):
            return role in ("client", "company")
        return role in ("client", "company")

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        role, user_id = payload.get("user_type"), payload.get("user_id")
        queryset = Device.objects.select_related("client", "current_company")
        if role == "client":
            queryset = queryset.filter(client_id=user_id)
        elif role == "company":
            queryset = queryset.filter(Q(current_company_id=user_id) | Q(current_company__isnull=True))
        return queryset.order_by("-created_at")

    def user_can_access_object(self, request, obj, payload):
        role, user_id = payload.get("user_type"), payload.get("user_id")
        if role == "admin" or request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if self.action == "create":
            return role == "client" and obj.client_id == user_id
        if self.action == "destroy":
            return role == "client" and obj.client_id == user_id
        return ((role == "client" and obj.client_id == user_id) or
                (role == "company" and obj.current_company_id in (None, user_id)))

    def perform_create(self, serializer):
        payload = self.request.auth.payload
        if payload.get("user_type") == "client":
            serializer.save(client_id=payload["user_id"])
        else:
            serializer.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        payload = self.request.auth.payload
        if payload.get("user_type") != "company":
            serializer.save()
            return

        offered_value = serializer.validated_data.get("offered_value")
        if offered_value is None:
            raise ValidationError({"offered_value": "Informe o valor da oferta."})

        save_kwargs = {}
        if instance.current_company_id is None:
            save_kwargs["current_company_id"] = payload["user_id"]
        if instance.offered_value is None:
            save_kwargs["device_status"] = Device.Status.OFFERED
            save_kwargs["offered_at"] = timezone.now()
        serializer.save(**save_kwargs)

    @action(detail=True, methods=("post",), url_path="respond")
    def respond(self, request, pk=None):
        device = self.get_object()
        accepted = request.data.get("accepted")
        if not isinstance(accepted, bool):
            raise ValidationError({"accepted": "Informe true ou false."})
        if device.device_status != Device.Status.OFFERED:
            raise ValidationError({"device_status": "Este dispositivo não possui uma oferta pendente."})

        device.device_status = Device.Status.ACCEPTED if accepted else Device.Status.REFUSED
        device.save(update_fields=("device_status",))
        return Response({"data": self.get_serializer(device).data}, status=status.HTTP_200_OK)
