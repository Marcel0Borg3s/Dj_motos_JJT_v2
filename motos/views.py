from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Moto, ImagemMoto  
from .forms import MotoForm

class MotosListView(ListView):
    model = Moto
    template_name = 'motos/motos_list.html'
    context_object_name = 'motos'

class MotoDetailView(DetailView):
    model = Moto
    template_name = 'motos/moto_detail.html'

class NewMotoCreateView(LoginRequiredMixin, CreateView):
    model = Moto
    form_class = MotoForm
    template_name = 'motos/moto_form.html'
    success_url = reverse_lazy('motos_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ImagemFormSet = inlineformset_factory(Moto, ImagemMoto, fields=('imagem',), extra=1)
        if self.request.POST:
            data['imagens_form'] = ImagemFormSet(self.request.POST, self.request.FILES)
        else:
            data['imagens_form'] = ImagemFormSet()
        return data

    def form_valid(self, form):
        form.instance.owner = self.request.user
        context = self.get_context_data()
        imagens_form = context['imagens_form']
        if imagens_form.is_valid():
            self.object = form.save()
            imagens_form.instance = self.object
            imagens_form.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Moto
    form_class = MotoForm
    template_name = 'motos/moto_form.html'
    success_url = reverse_lazy('motos_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ImagemFormSet = inlineformset_factory(Moto, ImagemMoto, fields=('imagem',), extra=1, can_delete=True)
        if self.request.POST:
            data['imagens_form'] = ImagemFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['imagens_form'] = ImagemFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        imagens_form = context['imagens_form']
        if imagens_form.is_valid():
            self.object = form.save()
            imagens_form.instance = self.object
            imagens_form.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Moto
    template_name = 'motos/moto_delete.html'
    success_url = reverse_lazy('motos_list')
