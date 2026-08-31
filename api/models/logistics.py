#Importando os modelinhos do django
from django.db import models

#Importando todos as classes de usuários e a classe de dispositivos
from users.models import Client, Company, Driver
from devices.models import Device

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
    chatId = models.CharField(max_length=100, blank=True, null=True)
    requestDate = models.DateTimeField(auto_now_add=True)
    currentStatus = models.CharField(max_length=25,choices=RequestStatus.choices,default=RequestStatus.REQUESTED)
    updatedAt = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "return_request"
    def __str__(self):
        return f"Solicitação #{self.pk} ({self.currentStatus})"

#Classe do Histórioco da Requisição
class RequestStatusHistory(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=25, choices=RequestStatus.choices)
    changedAt = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = "request_status_history"
        ordering = ["changedAt"]
    def __str__(self):
        return f"Solicitação #{self.return_request_id} -> {self.status}"
