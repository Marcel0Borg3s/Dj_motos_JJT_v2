from motos.models import Motos
from motos.forms import MotoModelForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

class MotosListView(ListView):
    model = Motos
    template_name = 'motos.html'
    context_object_name = 'motos'

    def get_queryset(self):
        motos = super().get_queryset().order_by('model')
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

    
    