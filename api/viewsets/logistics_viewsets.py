from api.auth.permissions import TokenUserPermission
from api.models import ReturnRequest, Ride, RequestStatusHistory, RideStatusHistory
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


class RequestStatusHistoryViewSet(ScopedLogisticsViewSet):
    model = RequestStatusHistory
    serializer_class = RequestStatusHistorySerializer
    filterset_fields = ("return_request", "status")


class RideStatusHistoryViewSet(ScopedLogisticsViewSet):
    model = RideStatusHistory
    serializer_class = RideStatusHistorySerializer
    filterset_fields = ("ride", "status")
