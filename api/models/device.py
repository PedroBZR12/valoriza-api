from django.db import models
from django.core.exceptions import ValidationError
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
    device_category=models.CharField(max_length=5,choices=Category.choices)
    device_condition=models.CharField(max_length=5,choices=Condition.choices)
    device_status=models.CharField(max_length=10,choices=Status.choices,default=Category.IN_ANALISYS)
    device_model=models.CharField(max_length=100)
    device_description=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    offered_at=models.DateTimeField(null=True,blank=True)

    class Meta:
        db_table = "device"

    #Bloqueios de alteração
    #Sobreescrevendo a função save para não deixá-la ser aplicada em device_condition e offered_value
    def save(self, *args, **kwargs):
        if self.pk:
            update=Device.objects.get(pk=self.pk)
            if self.device_condition != update.device_condition:
                raise ValidationError("A condição do dispositivo não pode ser alterada!")
            if self.offered_value is not None and update.offered_value:
                raise ValidationError("A oferta não pode ser alterada depois de proposta!")
            super().save(*args,**kwargs)
    
    def __str__(self):
        return f"{self.device_category} - {self.device_model or 'sem modelo'}"
