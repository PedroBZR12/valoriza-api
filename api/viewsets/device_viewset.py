from rest_framework import viewsets
from django.db.models import Q

from api.auth.permissions import TokenUserPermission
from api.models import Device
from api.serializers.device_serializer import DeviceSerializer
from api.viewsets.base import ApiModelViewSet


class DeviceViewSet(ApiModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = (TokenUserPermission,)
    filterset_fields = ("device_category", "device_condition", "device_status", "client", "current_company")
    ordering_fields = ("created_at", "offered_value", "device_model")
    ordering = ("-created_at",)

    def can_perform_action(self, request, payload):
        return payload.get("user_type") in ("client", "company", "admin") and not (
            self.action == "create" and payload.get("user_type") != "client")

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
        if payload.get("user_type") == "company" and instance.current_company_id is None:
            serializer.save(current_company_id=payload["user_id"])
        else:
            serializer.save()
