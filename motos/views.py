from motos.models import Motos
from motos.forms import MotoModelForm
from django.views.generic import CreateView, ListView 

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

class NewMotoCreateView(CreateView):
    model = Motos
    form_class = MotoModelForm
    template_name = 'new_moto.html'
    success_url = '/motos/'

