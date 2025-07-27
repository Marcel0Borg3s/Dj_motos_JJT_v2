"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from motos.views import motos_view, new_moto_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('motos/', motos_view, name='motos_list'),
    path('new_moto/', 'new_moto_view', name='new_moto'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


