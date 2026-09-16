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

#Tabela "Compania"
class Company(models.Model):
  company_name=models.CharField(max_length=127)
  company_adress=models.CharField(max_length=255)
  company_cnpj=models.CharField(max_length=18, unique=True)
  company_email=models.CharField(max_length=127, unique=True)
  company_password_hash=models.CharField(max_length=255)
  company_account_created_at=models.DateTimeField(auto_now_add=True)
  class Meta:
    db_table="company"
  def __str__(self):
    return self.company_name
