# agendamiento/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def pagina_inicio(request):
    return render(request, 'agendamiento/inicio.html')