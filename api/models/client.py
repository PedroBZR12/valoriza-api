#Importando a biblioteca de banco de dados django
from django.db import models

#Parâmetros de Padronização:
#Campos de Nome e de Email aceitam 127 caracteres
#Campos de CPF aceitam 11 caracteres
#Campos de CNPJ aceitam 18 caracteres
#Campos de CNH aceitam 9 caracteres
#Campos de Endereço e de Hash de senha aceitam 255 caracteres

#O método Meta vai definir estritamente o nome da tabela no django
#e o método __str__(self) (nome horroroso, jesus) vai devolver a string 
#nome ao invés do objeto na hora de chamar no debug.

#Tabela "Cliente"
class Client(models.Model):
  clientName=models.CharField(max_length=127)
  clientAdress=models.CharField(max_length=255)
  clientCPF=models.CharField(max_length=11, unique=True)
  clientEmail=models.CharField(max_length=127, unique=True)
  clientPasswordHash=models.CharField(max_length=255)
  clientAccountCreatedAt=models.DateTimeField(auto_now_add=True)
  class Meta:
    db_table="client"
  def __str__(self):
    return self.clientName
