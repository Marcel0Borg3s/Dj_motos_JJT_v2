"""
Sinais do módulo stockcontrol.

Cria automaticamente um registro MotoStock vazio sempre que
uma nova moto for cadastrada no sistema.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from motos.models import Motos
from stockcontrol.models import MotoStock


@receiver(post_save, sender=Motos)
def criar_stock_ao_cadastrar_moto(sender, instance, created, **kwargs):
    """
    Cria um registro MotoStock automaticamente para cada nova moto.

    Args:
        instance: A moto recém-criada.
        created: True se foi criada agora, False se só atualizada.
    """
    if created:
        MotoStock.objects.get_or_create(moto=instance)
