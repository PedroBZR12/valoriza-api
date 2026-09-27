#Importando os modelinhos do django
from django.db import models
from api.models.client import Client
from api.models.company import Company
from api.models.deliverydriver import Driver
from api.models.device import Device

#Estados possíveis da requisição
class RequestStatus(models.TextChoices):
    REQUESTED = "Solicitado"
    ACCEPTED = "Aceito"
    COLLECTED = "Coletado"
    IN_TRANSIT = "Em trânsito"
    RECEIVED_BY_COMPANY = "Recebido pela empresa"
    EVALUATED = "Avaliado"
    COMPLETED = "Concluído"
    CANCELLED = "Cancelado"

#Classe da Requisição
class ReturnRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTEC, related_name="return_requests")
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="return_requests")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="return_requests")
    device = models.OneToOneField(Device, on_delete=models.PROTECT, related_name="return_request")
    chat_id = models.CharField(max_length=100, blank=True, null=True)
    request_date = models.DateTimeField(auto_now_add=True)
    current_status = models.CharField(max_length=25,choices=RequestStatus.choices,default=RequestStatus.REQUESTED)
    updated_at = models.DateTimeField(auto_now=True)
#Estados possíveis da corrida
class RideStatus(models.TextChoices):
    AGUARDANDO_MOTORISTA = "AGUARDANDO_MOTORISTA", "Aguardando motorista"
    MOTORISTA_ACEITOU = "MOTORISTA_ACEITOU", "Motorista aceitou"
    PRODUTO_RECOLHIDO = "PRODUTO_RECOLHIDO", "Produto recolhido"
    EM_TRANSITO = "EM_TRANSITO", "Em trânsito"
    ENTREGUE = "ENTREGUE", "Entregue"
    CANCELADA = "CANCELADA", "Cancelada"

#Classe da Corrida
class Ride(models.Model):
    #Vínculos exigidos pelos critérios de aceite do ticket
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="rides")  # origem
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="rides")  # destino
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="rides")
    device = models.OneToOneField(Device, on_delete=models.PROTECT, related_name="ride")  # componente

    chat_id = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=25, choices=RideStatus.choices, default=RideStatus.AGUARDANDO_MOTORISTA)

    #Datas relevantes
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ride"

    def __str__(self):
        return f"Corrida #{self.pk} ({self.get_current_status_display()})"

#Classe do Histórioco da Requisição
class RequestStatusHistory(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=25, choices=RequestStatus.choices)
#Classe do Histórico de status da Corrida
class RideStatusHistory(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=25, choices=RideStatus.choices)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "ride_status_history"
        ordering = ["changed_at"]

    def __str__(self):
        return f"Corrida #{self.ride_id} -> {self.status}"
