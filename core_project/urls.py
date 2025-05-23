# core_project/urls.py
from django.contrib import admin
from django.urls import path, include
from agendamiento import views as agendamiento_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agendamiento/', include('agendamiento.urls', namespace='agendamiento')),
    path('', agendamiento_views.pagina_inicio, name='pagina_inicio'),
]