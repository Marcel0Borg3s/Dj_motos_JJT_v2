from django.shortcuts import render
from motos.models import Motos
from motos.forms import MotoForm

def motos_view(request):
    motos = Motos.objects.all().order_by('model')
    search = request.GET.get('search')

    if search:
        motos = motos.filter(model__contains=search)

    return render(
        request, 
        'motos.html', 
        {'motos': motos }

    )

def new_moto_view(request):
    new_moto_form = MotoForm()
    return render(request, 'new_moto.html', {'form': new_moto_form})



