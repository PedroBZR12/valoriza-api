from django.db import models
from api.models.client import Client
from api.models.company import Company

class Device(models.Model):
    #Achei no site do ReciclaSampa categorias de descarte de lixo eletrônico, acho que fica melhor do que ter que fazer o usuário inventar uma categoria da cabeça dele
    #Categoria do Dispositivo
    class Category(models.TextChoices):
        GREEN="GREEN","Computadores, Tablets, Celulares"
        WHITE="WHITE","Geladeiras, Micro-ondas, Máquina de Lavar"
        BROWN="BROWN","Televisão, Rádio, Câmeras e Caixas de Som"
        BLUE="BLUE","Ferramentas Elétricas, Brinquedos eletrônicos"
        OFF_CATEGORIES="OTHER","Meu dispositivo não se encaixa nas categorias acima"
    
    #Condição do aparelho
    class Condition(models.TextChoices):
        NEW="NOVO","Novo"
        USED="USADO","Usado"

    #Status da oferta do dispositivo
    class Status(models.TextChoices):
        IN_ANALISYS="EM_ANALISE","Em análise"
        OFFERED="OFERTADO","Ofertado"
        ACCEPTED="ACEITO","Aceito"
        REFUSED="RECUSADO","Recusado"

    #Relações 1:N entre clientes/empresas e dispositivos
    client=models.ForeignKey(Client, on_delete=models.CASCADE)
    current_company=models.ForeignKey(Company, on_delete=models.SET_Null, null=True, blank=True)

    #Variáveis do dispositivo
    expected_offer=models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True) #O cliente pode opcionalmente colocar um valor de oferta esperado de até R$9.999,99.
    offered_value=models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  #A empresa faz uma oferta de até R$9.999,99.
    device_category=models.CharField(max_lenght=5,choices=Category.choices)
    device_condition=models.CharField(max_lenght=5,choices=Condition.choices)
    device_status=models.CharField(max_lenght=10,choices=Status.choices)
    device_model=models.CharField(max_length=100)
    device_description=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "device"

    def __str__(self):
        return f"{self.device_category} - {self.device_model or 'sem modelo'}"
