from django.db import models
from api.models.device import Device
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
