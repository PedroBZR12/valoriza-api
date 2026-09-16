from django.db import models
from api.models.client import Client
from api.models.company import Company
from api.models.device import Device


class Offer(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDENTE", "Pendente"
        ACCEPTED = "ACEITA", "Aceita"
        REJECTED = "RECUSADA", "Recusada"
        EXPIRED = "EXPIRADA", "Expirada"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="offers")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="offers")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="offers")
    offered_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "offer"

    def __str__(self):
        return f"Oferta #{self.pk} - {self.company} → {self.client} ({self.status})"
