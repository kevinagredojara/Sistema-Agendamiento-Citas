# agendamiento/urls.py
from django.urls import path, reverse_lazy 
from django.contrib.auth import views as auth_views

app_name = 'agendamiento'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='agendamiento/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # URLs para cambio de contraseña
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='agendamiento/password_change_form.html',
             success_url=reverse_lazy('agendamiento:password_change_done') # <--- CORRECCIÓN AQUÍ
         ),
         name='password_change'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='agendamiento/password_change_done.html'
         ),
         name='password_change_done'),
]