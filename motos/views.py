from django.shortcuts import render, redirect
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
    if request.method == 'POST':
        new_moto_form = MotoForm(request.POST, request.FILES)
        if new_moto_form.is_valid():
            new_moto_form.save()
            return redirect('motos_view')
         
    else:
        new_moto_form = MotoForm()
    return render(request, 'new_moto.html', { 'new_moto_form': new_moto_form})

