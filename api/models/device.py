from django.db import models
from api.models.client import Client
from api.models.company import Company

class Device(models.Model):
    device_category = models.CharField(max_length=45)
    device_model = models.CharField(max_length=100)
    device_description = models.CharField(max_length=255)
    offered_value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    #Condição do aparelho
    class Condition(models.TextChoices):
        NEW="Novo"
        USED="Usado"

    #Status da oferta do dispositivo
    class Status(models.TextChoices):
        IN_ANALISYS="Em análise"
        OFFERED="Ofertado"
        ACCEPTED="Aceito"
        REFUSED="Recusado"

    class Meta:
        db_table = "device"

    def __str__(self):
        return f"{self.device_category} - {self.device_model or 'sem modelo'}"
