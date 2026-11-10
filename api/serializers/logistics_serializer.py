from rest_framework import serializers

from api.models import ReturnRequest, Ride, RequestStatusHistory, RideStatusHistory


class ParticipantValidationMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        token = getattr(request, "auth", None) if request else None
        payload = getattr(token, "payload", {}) if token else {}
        role, user_id = payload.get("user_type"), payload.get("user_id")
        if role == "admin":
            return attrs
        if self.Meta.model in (ReturnRequest, Ride):
            client = attrs.get("client", getattr(self.instance, "client", None))
            company = attrs.get("company", getattr(self.instance, "company", None))
            driver = attrs.get("driver", getattr(self.instance, "driver", None))
            device = attrs.get("device", getattr(self.instance, "device", None))
            if device and client and device.client_id != client.pk:
                raise serializers.ValidationError({"device": "O dispositivo deve pertencer ao cliente informado."})
            if device and company and device.current_company_id not in (None, company.pk):
                raise serializers.ValidationError({"device": "O dispositivo está associado a outra empresa."})
        else:
            parent_key = "return_request" if self.Meta.model == RequestStatusHistory else "ride"
            parent = attrs.get(parent_key, getattr(self.instance, parent_key, None))
            client = getattr(parent, "client", None)
            company = getattr(parent, "company", None)
            driver = getattr(parent, "driver", None)
        if role == "client" and getattr(client, "pk", None) != user_id:
            raise serializers.ValidationError("O registro deve pertencer ao cliente autenticado.")
        if role == "company" and getattr(company, "pk", None) != user_id:
            raise serializers.ValidationError("O registro deve pertencer à empresa autenticada.")
        if role == "driver" and getattr(driver, "pk", None) != user_id:
            raise serializers.ValidationError("O registro deve pertencer ao motorista autenticado.")
        return attrs


class ReturnRequestSerializer(ParticipantValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = "__all__"
        read_only_fields = ("id", "request_date", "updated_at")


class RideSerializer(ParticipantValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = "__all__"
        read_only_fields = ("id", "requested_at", "updated_at")


class RequestStatusHistorySerializer(ParticipantValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = RequestStatusHistory
        fields = "__all__"
        read_only_fields = ("id", "changed_at")


class RideStatusHistorySerializer(ParticipantValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = RideStatusHistory
        fields = "__all__"
        read_only_fields = ("id", "changed_at")
