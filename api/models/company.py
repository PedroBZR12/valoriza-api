from django.db import models
class Company(models.Model):
  id=models.AutoField(primary_key=True)
  company_name=models.CharField(maxlenght=255)
  cnpj=models.CharField(maxlenght=18, unique=True)
  
