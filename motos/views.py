from django.shortcuts import render
from motos.models import Motos

def motos_view(request):
    motos = Motos.objects.all()

    return render(
        request, 
        'motos.html', 
        {'motos': motos }

    )


