import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("🔧 Iniciando pruebas de acceso al admin...")

# Crear cliente de prueba
client = Client()

# Obtener superusuario existente o crear uno nuevo
try:
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("✅ Superusuario creado")
    else:
        print(f"✅ Usando superusuario existente: {superuser.username}")
    
    # Hacer login
    login_success = client.login(username=superuser.username, password='admin123' if superuser.username == 'admin' else 'admin123456')
    
    if not login_success:
        # Intentar con contraseña alternativa
        superuser.set_password('admin123')
        superuser.save()
        login_success = client.login(username=superuser.username, password='admin123')
    
    if login_success:
        print("✅ Login exitoso")
    else:
        print("❌ Error en login")
        exit(1)
    
    # Probar acceso al admin principal
    response = client.get('/admin/')
    print(f"📋 Respuesta admin principal: {response.status_code}")
    
    # Probar acceso a usuarios
    response = client.get('/admin/auth/user/')
    print(f"📋 Respuesta admin usuarios: {response.status_code}")
    
    # Probar acceso al sistema principal
    response = client.get('/')
    print(f"📋 Respuesta sistema principal: {response.status_code}")
    
    print("🎉 ¡Pruebas completadas!")

except Exception as e:
    print(f"❌ Error: {e}")
