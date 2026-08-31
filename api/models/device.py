from django.db import models

class Device(models.Model):
    deviceCategory = models.CharField(max_length=45)
    deviceModel = models.CharField(max_length=100)
    deviceDescription = models.CharField(max_length=255)
    offeredValue = models.DecimalField(max_digits=10, decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "device"
    def __str__(self):
        return f"{self.deviceCategory} - {self.deviceModel or 'sem modelo'}"
