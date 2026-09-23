from django.db import models
from api.models.client import Client
from api.models.company import Company

class Device(models.Model):
    device_model = models.CharField(max_length=100)
    device_description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    #Achei no site do ReciclaSampa categorias de descarte de lixo eletrônico, acho que fica melhor do que ter que fazer o usuário inventar uma categoria da cabeça dele
    class Category(models.TextChoices):
        GREEN="Computadores, Tablets, Celulares"
        WHITE="Geladeiras, Micro-ondas, Máquina de Lavar"
        BROWN="Televisão, Rádio, Câmeras e Caixas de Som"
        BLUE="Ferramentas Elétricas, Brinquedos eletrônicos"
        OFF_CATEGORIES="Meu dispositivo não se encaixa nas categorias acima"
    
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

    #O cliente pode colocar um valor de oferta esperado de até R$9.999,99
    expected_offer=models.DecimalField(max_digits=6, decimal_places=2)

    #Isso aqui faz a relação 1:N de clientes e dispositivos (um cliente pode querer ofertar vários dispositivos)
    client=models.ForeignKey(Client, on_delete=models.CASCADE)
    #E isso faz a relação 1:N de empresas e dispositivos (uma empresa pode aceitar a oferta de vários dispositivos)
    current_company=models.ForeignKey(Company, on_delete=models.SET_Null, null=True, blank=True)

    class Meta:
        db_table = "device"

    def __str__(self):
        return f"{self.device_category} - {self.device_model or 'sem modelo'}"
