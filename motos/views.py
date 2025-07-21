from django.http import HttpResponse


def motos_view(request):
    return HttpResponse('Minhas motos')


