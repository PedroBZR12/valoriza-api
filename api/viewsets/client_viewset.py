from rest_framework import status, viewsets
from api.serializers.client_serializer import CreateClientSerializer, ClientSerializer
from rest_framework.response import Response

class ClientViewSet(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        serializer = CreateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = serializer.save()

        return Response(
            ClientSerializer(client).data,
            status=status.HTTP_201_CREATED
        )