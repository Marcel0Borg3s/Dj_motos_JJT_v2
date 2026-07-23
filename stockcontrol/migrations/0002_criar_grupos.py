"""
Data migration: cria os grupos de permissão 'financeiro' e 'gerente'.

Executado automaticamente ao aplicar as migrations.
"""

from django.db import migrations


def criar_grupos(apps, schema_editor):
    """Cria os grupos financeiro e gerente se não existirem."""
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Grupo financeiro (acesso total ao estoque)
    Group.objects.get_or_create(name='financeiro')

    # Grupo gerente (CRUD de motos)
    Group.objects.get_or_create(name='gerente')


def reverter_grupos(apps, schema_editor):
    """Remove os grupos criados (rollback)."""
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['financeiro', 'gerente']).delete()


class Migration(migrations.Migration):
    """Aplica a criação dos grupos financeiro e gerente."""

    dependencies = [
        ('stockcontrol', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, reverter_grupos),
    ]
