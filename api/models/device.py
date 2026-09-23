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

    #Isso aqui faz a relação 1:N de clientes e dispositivos (um cliente pode querer ofertar vários dispositivos)
    client=models.ForeignKey(Client, on_delete=models.CASCADE)
    #E isso faz a relação 1:N de empresas e dispositivos (uma empresa pode aceitar a oferta de vários dispositivos)
    current_company=models.ForeignKey(Company, on_delete=models.SET_Null, null=True, blank=True)

    class Meta:
        db_table = "device"

    def __str__(self):
        return f"{self.device_category} - {self.device_model or 'sem modelo'}"
