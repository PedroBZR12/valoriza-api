from rest_framework import viewsets
from api.models import Offer
from api.serializers.offer_serializer import OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().order_by('-created_at')
    serializer_class = OfferSerializer
