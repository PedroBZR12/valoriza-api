from rest_framework import serializers
from api.models import Offer


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_offered_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor ofertado deve ser maior que zero.")
        return value
