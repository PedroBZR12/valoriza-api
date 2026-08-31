from django.db import models
class Deliverydriver(models.Model):
  id=models.AutoField(primary_key=True)
  driver_name=models.CharField(maxlenght=255)
  cpf=models.CharField(maxlenght=11, unique=True)
