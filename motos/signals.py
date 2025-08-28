from django.core.files import File
from django.db.models.signals import post_save, post_delete, pre_save
from django.db.models import Sum
from django.dispatch import receiver
from motos.models import Motos, MotoInventory
import os

def moto_inventory_update():
    motos_count = Motos.objects.all().count()
    motos_value = Motos.objects.aggregate(
        total_value=Sum('value')
    )['total_value']
    MotoInventory.objects.create(
        motos_count=motos_count,
        motos_value=motos_value
    )


@receiver(post_save, sender=Motos)
def moto_post_save(sender, instance, **kwargs):
    moto_inventory_update()

@receiver(post_delete, sender=Motos)
def moto_post_delete(sender, instance, **kwargs):
    moto_inventory_update()

@receiver(pre_save, sender=Motos)
def moto_presave(sender, instance, **kwargs):
    # Se não tiver bio, define um texto padrão
    if not instance.bio:
        instance.bio = "Entre em contato!"

   