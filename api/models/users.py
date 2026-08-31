#Importando a biblioteca de banco de dados django
from django.db import models

#Parâmetros de Padronização:
#Campos de Nome e de Email aceitam 127 caracteres
#Campos de CPF aceitam 11 caracteres
#Campos de CNPJ aceitam 18 caracteres
#Campos de CNH aceitam 9 caracteres
#Campos de Endereço e de Hash de senha aceitam 255 caracteres

#Tabela "Cliente"
class Client(models.Model):
  clientName=models.CharField(max_length=127)
  clientAdress=models.CharField(max_length=255)
  clientCPF=models.CharField(max_length=11, unique=TRUE)
  clientEmail=models.CharField(max_length=127, unique=TRUE)
  clientPasswordHash=models.CharField(max_length=255)
  clientAccountCreatedAt=models.DatetimeField(auto_now_add=True)
  class Meta:
    db_table="client"
  def __str__(self):
    return self.clientName

#Tabela "Compania"
class Company(models.Model):
  companyName=models.CharField(max_length=127)
  companyAdress=models.CharField(max_length=255)
  companyCNPJ=models.CharField(max_length=18, unique=TRUE)
  companyEmail=models.CharField(max_length=127, unique=TRUE)
  companyPasswordHash=models.CharField(max_length=255)
  companyAccountCreatedAt=models.DateTimeField(auto_now_add=True)
  class Meta:
    db_table="company"
  def __str__(self):
    return self.companyName

#Tabela "Motorista"
class Driver(models.Model):
  driverName=models.CharField(max_length=127)
  driverCPF=models.CharField(max_length=11, unique=TRUE)
  driverCNH=models.CharField(max_length=9, unique=TRUE)
  driverEmail=models.CharField(max_length=127, unique=TRUE)
  driverPasswordHash=models.CharField(max_length=255)
  driverAccountCreatedAt=models.DateTimeField(auto_now_add=True)
  class Meta:
    db_table="driver"
  def __str__(self):
    return self.driverName

