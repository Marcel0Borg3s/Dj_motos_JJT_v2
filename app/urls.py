from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from motos.views import MotosView, NewMotoView
from accounts.views import register_view, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('motos/', MotosView.as_view(), name='motos_list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('new_moto/', NewMotoView.as_view(), name='new_moto'),
    path('register/', register_view, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 