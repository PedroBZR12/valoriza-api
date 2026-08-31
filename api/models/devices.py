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


class DeviceImage(models.Model):
    class ImageType(models.TextChoices):
        INITIAL = "initial", "Foto inicial (oferta)"
        CONFIRMATION = "confirmation", "Foto de confirmação (entrega)"
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="images")
    imageUrl = models.URLField(max_length=255)
    imageType = models.CharField(max_length=20, choices=ImageType.choices)
    uploadedAt = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "device_image"
    def __str__(self):
        return f"Imagem #{self.pk} ({self.imageType}) - Device #{self.device_id}"
