from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.auth.permissions import TokenUserPermission
from api.models import ReturnRequest, Ride, RequestStatusHistory, RideStatusHistory
from api.models.logistics import RideStatus
from api.serializers.logistics_serializer import (
    ReturnRequestSerializer, RideSerializer,
    RequestStatusHistorySerializer, RideStatusHistorySerializer,
)
from api.viewsets.base import ApiModelViewSet


class ScopedLogisticsViewSet(ApiModelViewSet):
    permission_classes = (TokenUserPermission,)
    model = None
    serializer_class = None

    def _participation_filter(self, queryset, role, user_id):
        if role == "client":
            return queryset.filter(client_id=user_id) if self.model in (ReturnRequest, Ride) else queryset.filter(
                **{"return_request__client_id" if self.model == RequestStatusHistory else "ride__client_id": user_id})
        if role == "company":
            return queryset.filter(company_id=user_id) if self.model in (ReturnRequest, Ride) else queryset.filter(
                **{"return_request__company_id" if self.model == RequestStatusHistory else "ride__company_id": user_id})
        if role == "driver":
            if self.model == Ride:
                return queryset.filter(Q(driver_id=user_id) | Q(driver__isnull=True))
            return queryset.filter(driver_id=user_id) if self.model in (ReturnRequest, Ride) else queryset.filter(
                **{"return_request__driver_id" if self.model == RequestStatusHistory else "ride__driver_id": user_id})
        return queryset

    def get_queryset(self):
        payload = self.request.auth.payload if self.request.auth else {}
        queryset = self.model.objects.all()
        if payload.get("user_type") != "admin":
            queryset = self._participation_filter(queryset, payload.get("user_type"), payload.get("user_id"))
        return queryset

    def can_perform_action(self, request, payload):
        if self.action in ("accept", "pickup", "deliver"):
            return payload.get("user_type") == "driver"
        if self.action != "create":
            return True
        return payload.get("user_type") in ("client", "company", "admin")

    def user_can_access_object(self, request, obj, payload):
        if payload.get("user_type") == "admin" or request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if self.model == ReturnRequest:
            return ((payload.get("user_type") == "client" and obj.client_id == payload.get("user_id")) or
                    (payload.get("user_type") == "company" and obj.company_id == payload.get("user_id")) or
                    (payload.get("user_type") == "driver" and obj.driver_id == payload.get("user_id")))
        if self.model == Ride:
            if (self.action == "accept" and payload.get("user_type") == "driver" and
                    obj.driver_id is None):
                return obj.current_status == RideStatus.AGUARDANDO_MOTORISTA
            return ((payload.get("user_type") == "client" and obj.client_id == payload.get("user_id")) or
                    (payload.get("user_type") == "company" and obj.company_id == payload.get("user_id")) or
                    (payload.get("user_type") == "driver" and obj.driver_id == payload.get("user_id")))
        parent = obj.return_request if self.model == RequestStatusHistory else obj.ride
        return ((payload.get("user_type") == "client" and parent.client_id == payload.get("user_id")) or
                (payload.get("user_type") == "company" and parent.company_id == payload.get("user_id")) or
                (payload.get("user_type") == "driver" and parent.driver_id == payload.get("user_id")))


class ReturnRequestViewSet(ScopedLogisticsViewSet):
    model = ReturnRequest
    serializer_class = ReturnRequestSerializer
    filterset_fields = ("current_status", "client", "company", "driver", "device")
    ordering_fields = ("request_date", "updated_at")
    ordering = ("-request_date",)


class RideViewSet(ScopedLogisticsViewSet):
    model = Ride
    serializer_class = RideSerializer
    filterset_fields = ("current_status", "client", "company", "driver", "device")
    ordering_fields = ("requested_at", "updated_at")
    ordering = ("-requested_at",)

    def can_perform_action(self, request, payload):
        if self.action == "create":
            return payload.get("user_type") in ("client", "admin")
        return super().can_perform_action(request, payload)

    @action(detail=True, methods=("post",), url_path="accept")
    def accept(self, request, pk=None):
        ride = self.get_object()
        with transaction.atomic():
            ride = Ride.objects.select_for_update().get(pk=ride.pk)
            if (ride.driver_id is not None or
                    ride.current_status != RideStatus.AGUARDANDO_MOTORISTA):
                raise ValidationError({"current_status": "Esta corrida não está mais disponível."})

            ride.driver_id = request.auth.payload["user_id"]
            ride.current_status = RideStatus.MOTORISTA_ACEITOU
            ride.accepted_at = timezone.now()
            ride.save(update_fields=("driver", "current_status", "accepted_at", "updated_at"))
            RideStatusHistory.objects.create(
                ride=ride,
                status=ride.current_status,
                notes="Corrida aceita pelo motorista.",
            )

        return Response({"data": self.get_serializer(ride).data}, status=status.HTTP_200_OK)

    def _transition_ride(self, request, pk, allowed_statuses, next_status, timestamp_field):
        ride = self.get_object()
        with transaction.atomic():
            ride = Ride.objects.select_for_update().get(pk=ride.pk)
            if ride.current_status not in allowed_statuses:
                raise ValidationError({"current_status": "A corrida não pode avançar deste status."})

            ride.current_status = next_status
            setattr(ride, timestamp_field, timezone.now())
            ride.save(update_fields=("current_status", timestamp_field, "updated_at"))
            RideStatusHistory.objects.create(ride=ride, status=next_status)

        return Response({"data": self.get_serializer(ride).data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",), url_path="pickup")
    def pickup(self, request, pk=None):
        return self._transition_ride(
            request, pk, (RideStatus.MOTORISTA_ACEITOU,),
            RideStatus.PRODUTO_RECOLHIDO, "collected_at",
        )

    @action(detail=True, methods=("post",), url_path="deliver")
    def deliver(self, request, pk=None):
        return self._transition_ride(
            request, pk, (RideStatus.PRODUTO_RECOLHIDO, RideStatus.EM_TRANSITO),
            RideStatus.ENTREGUE, "delivered_at",
        )


class RequestStatusHistoryViewSet(ScopedLogisticsViewSet):
    model = RequestStatusHistory
    serializer_class = RequestStatusHistorySerializer
    filterset_fields = ("return_request", "status")


class RideStatusHistoryViewSet(ScopedLogisticsViewSet):
    model = RideStatusHistory
    serializer_class = RideStatusHistorySerializer
    filterset_fields = ("ride", "status")
