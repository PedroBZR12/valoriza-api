from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.viewsets.auth_viewset import AuthViewSet
from api.viewsets.device_viewset import DeviceViewSet
from api.viewsets.offer_viewset import OfferViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
]
