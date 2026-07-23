from motos.models import Motos
from motos.forms import MotoModelForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
import json, urllib.request, urllib.error

from stockcontrol.models import MotoStock


class MotosListView(ListView):
    model = Motos
    template_name = 'motos.html'
    context_object_name = 'motos'

    def get_queryset(self):
        """
        Retorna as motos visíveis no site público.

        - Motos com stock oculto (sale_status='hidden') são excluídas.
        - Motos vendidas (sale_status='sold') são incluídas mas o
          template pode exibir um badge "Vendida".
        """
        # Subquery para pegar o status do estoque de cada moto
        stock_status = MotoStock.objects.filter(
            moto=OuterRef('pk')
        ).values('sale_status')[:1]

        motos = super().get_queryset().annotate(
            stock_status=Subquery(stock_status)
        ).order_by('model')

        # Exclui motos ocultas (hidden)
        motos = motos.exclude(stock_status='hidden')

        search = self.request.GET.get('search')
        if search:
            motos = motos.filter(model__icontains=search)

        return motos

@method_decorator(login_required(login_url='login'), name='dispatch')
class NewMotoCreateView(CreateView):
    model = Motos
    form_class = MotoModelForm
    template_name = 'new_moto.html'
    success_url = '/motos/'

class MotoDetailView(DetailView):
    model = Motos
    template_name = 'moto_detail.html'

    def get_queryset(self):
        """Anota o status do estoque para exibir badge de venda."""
        stock_status = MotoStock.objects.filter(
            moto=OuterRef('pk')
        ).values('sale_status')[:1]
        return super().get_queryset().annotate(
            stock_status=Coalesce(Subquery(stock_status), Value('available'))
        )

@method_decorator(login_required(login_url='login'), name='dispatch')
class MotoUpdateView(UpdateView):
    model = Motos
    form_class = MotoModelForm
    template_name = 'moto_update.html'
    def get_success_url(self):
        return reverse_lazy('moto_detail', kwargs={'pk': self.object.pk})

@method_decorator(login_required(login_url='login'), name='dispatch')
class MotoDeleteView(DeleteView):
    model = Motos
    template_name = 'moto_delete.html'
    success_url = '/motos/'


@login_required(login_url='login')
def generate_description(request):
    """
    Gera uma descrição técnica para uma moto usando OpenRouter (modelo gratuito).
    Recebe os dados via POST e retorna o texto gerado como JSON.
    """
    if request.method != 'POST':
        return HttpResponse('Método não permitido.', status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('JSON inválido.', status=400)

    # Monta o prompt com os dados disponíveis
    brand = data.get('brand', '').strip()
    model = data.get('model', '').strip()
    factor_year = data.get('factor_year', '').strip()
    model_year = data.get('model_year', '').strip()

    parts = []
    if brand: parts.append(f"Marca: {brand}")
    if model: parts.append(f"Modelo: {model}")
    if factor_year: parts.append(f"Ano de fabricação: {factor_year}")
    if model_year: parts.append(f"Ano do modelo: {model_year}")

    dados = '\n'.join(parts) if parts else 'Nenhum dado informado.'

    prompt = f"""Você é um redator especializado em anúncios de motos. Gere uma descrição técnica profissional e atrativa para o seguinte anúncio:

{dados}

A descrição deve:
- Ser em português do Brasil
- Ter entre 3 e 6 frases
- Destacar os pontos fortes da moto
- Usar tom profissional mas acessível
- Convidar o interessado a entrar em contato
- Para motos de alta cilindrada, incluir a cavalaria de forma destacada (ex: "moto com impressionantes XXX hp")
- Para motos de baixa cilindrada, destacar o baixo consumo de combustível (ex: "até XX km/l")
- Não incluir o valor/preço na descrição
- Não usar markdown, apenas texto plano
"""

    api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'API key não configurada.'}, status=500)

    payload = json.dumps({
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "messages": [
            {"role": "system", "content": "Você é um especialista em motos que cria descrições técnicas para anúncios."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': request.build_absolute_uri('/') or 'http://localhost:8000',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            description = result['choices'][0]['message']['content'].strip()
            return JsonResponse({'description': description})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        return JsonResponse({'error': f'Erro HTTP {e.code}: {error_body}'}, status=502)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
    