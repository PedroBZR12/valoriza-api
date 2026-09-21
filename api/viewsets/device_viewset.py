from rest_framework import viewsets
from api.models import Device
from api.serializers.device_serializer import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer