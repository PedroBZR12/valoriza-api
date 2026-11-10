from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.viewsets.auth_viewset import AuthViewSet
from api.viewsets.client_viewset import ClientViewSet
from api.viewsets.company_viewset import CompanyViewSet
from api.viewsets.device_image_viewset import DeviceImageViewSet
from api.viewsets.device_viewset import DeviceViewSet
from api.viewsets.driver_viewset import DriverViewSet
from api.viewsets.messages_viewset import MessageViewSet
from api.viewsets.logistics_viewsets import (
    ReturnRequestViewSet, RideViewSet,
    RequestStatusHistoryViewSet, RideStatusHistoryViewSet,
)


router = DefaultRouter()
router.register("auth", AuthViewSet, basename="auth")
router.register("clients", ClientViewSet, basename="client")
router.register("companies", CompanyViewSet, basename="company")
router.register("drivers", DriverViewSet, basename="driver")
router.register("chats", MessageViewSet, basename="chat")
router.register("devices", DeviceViewSet, basename="device")
router.register("device-images", DeviceImageViewSet, basename="device-image")
router.register("return-requests", ReturnRequestViewSet, basename="return-request")
router.register("rides", RideViewSet, basename="ride")
router.register("request-status-history", RequestStatusHistoryViewSet, basename="request-status-history")
router.register("ride-status-history", RideStatusHistoryViewSet, basename="ride-status-history")

urlpatterns = [
    # Alguns clientes POSTam sem a barra final; aliases evitam que o
    # CommonMiddleware tente redirecionar e descarte o corpo da requisição.
    path("auth/login", AuthViewSet.as_view({"post": "login"}), name="auth-login-no-slash"),
    path("auth/register", AuthViewSet.as_view({"post": "register"}), name="auth-register-no-slash"),
    path("auth/logout", AuthViewSet.as_view({"post": "logout"}), name="auth-logout-no-slash"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token-refresh-no-slash"),
    path("", include(router.urls)),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
