from django.shortcuts import render, redirect
from motos.models import Motos
from motos.forms import MotoModelForm
from django.views import View

class MotosView(View):
    def get(self, request):
        motos = Motos.objects.all().order_by('model')
        search = request.GET.get('search')

        if search:
            motos = motos.filter(model__contains=search)

        return render(
            request, 
            'motos.html', 
            {'motos': motos }
        )

class NewMotoView(View):

    def get(self, request):
        new_moto_form = MotoModelForm()
        return render(request, 'new_moto.html', { 'new_moto_form': new_moto_form})

    def post(self, request):
        new_moto_form = MotoModelForm(request.POST, request.FILES)
        if new_moto_form.is_valid():
            new_moto_form.save()
            return redirect('motos_list')
        return render(request, 'new_moto.html', { 'new_moto_form': new_moto_form})


