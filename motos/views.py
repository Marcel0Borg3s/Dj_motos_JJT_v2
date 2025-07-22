from django.shortcuts import render


def motos_view(request):
    return render(request, 
                  'motos.html', 
    )


