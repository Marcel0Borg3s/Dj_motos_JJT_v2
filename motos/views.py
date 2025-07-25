from django.shortcuts import render
from motos.models import Motos

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


