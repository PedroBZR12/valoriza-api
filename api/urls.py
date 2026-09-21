from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.viewsets.auth_viewset import AuthViewSet
from api.viewsets.device_viewset import DeviceViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'devices', DeviceViewSet, basename='device')


urlpatterns = [
    path('', include(router.urls)),
]