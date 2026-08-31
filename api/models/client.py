from django.db import models
class Client(models.Model):
  id=models.AutoField(primary_key=True)
  client_name=models.CharField(maxlenght=255)
  cpf=models.CharField(maxlenght=11, unique=True)
