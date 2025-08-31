from django.db import models
from django.contrib.auth.models import User

class Moto(models.Model):
    model = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    factor_year = models.IntegerField()
    model_year = models.IntegerField()
    plate = models.CharField(max_length=10, unique=True)
    value = models.FloatField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.model

class ImagemMoto(models.Model):
    moto = models.ForeignKey(Moto, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='motos_galeria/')

    def __str__(self):
        return f"Imagem para {self.moto.model}"
