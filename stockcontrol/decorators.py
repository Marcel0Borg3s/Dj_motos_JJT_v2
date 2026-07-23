"""
Decoradores de permissão para o sistema de Controle de Estoque.

Requisitos:
    - Usuário deve estar logado
    - Usuário deve pertencer ao grupo 'financeiro' OU ser superuser

Uso:
    @financeiro_required
    def minha_view(request):
        ...
    
    ou via URL:
    path('stock/', financeiro_required(MeuView.as_view()), name='...')
"""

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def is_financeiro(user):
    """
    Verifica se o usuário pertence ao grupo 'financeiro' ou é superuser.

    Args:
        user: Instância de User autenticado.

    Returns:
        bool: True se pode acessar o módulo financeiro.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='financeiro').exists()


def financeiro_required(view_func=None, redirect_url='login'):
    """
    Decorador que restringe acesso a usuários do grupo 'financeiro'.

    Args:
        view_func: Função ou classe view a ser decorada.
        redirect_url: URL para redirecionar se não autorizado.

    Uso como decorator de função:
        @financeiro_required
        def dashboard(request): ...

    Uso como decorator de classe (via method_decorator):
        @method_decorator(financeiro_required, name='dispatch')
        class DashboardView(View): ...
    """
    decorator = user_passes_test(
        is_financeiro,
        login_url=redirect_url,
        redirect_field_name=None,
    )
    if view_func:
        return decorator(view_func)
    return decorator
