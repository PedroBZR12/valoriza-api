from rest_framework import serializers

from api.models import Device, ReturnRequest, Ride, RequestStatusHistory, RideStatusHistory


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
            if self.Meta.model == Ride and device:
                existing_rides = Ride.objects.filter(device=device)
                if self.instance:
                    existing_rides = existing_rides.exclude(pk=self.instance.pk)
                if existing_rides.exists():
                    raise serializers.ValidationError({"device": "Já existe uma corrida para este dispositivo."})
            if self.Meta.model == Ride and self.instance is None:
                if role != "client":
                    raise serializers.ValidationError("Somente o cliente pode solicitar a coleta.")
                if not device or not company or device.current_company_id != company.pk:
                    raise serializers.ValidationError({
                        "device": "A empresa deve corresponder à oferta aceita para este equipamento."
                    })
                if device.device_status != Device.Status.ACCEPTED:
                    raise serializers.ValidationError({
                        "device": "A oferta do equipamento precisa ser aceita antes da coleta."
                    })
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
    device_model = serializers.CharField(source="device.device_model", read_only=True)
    device_category = serializers.CharField(source="device.device_category", read_only=True)
    device_condition = serializers.CharField(source="device.device_condition", read_only=True)
    device_image = serializers.URLField(
        source="device.device_image", read_only=True, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Ride
        fields = "__all__"
        read_only_fields = ("id", "driver", "current_status", "requested_at", "accepted_at",
                            "collected_at", "delivered_at", "updated_at")


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
