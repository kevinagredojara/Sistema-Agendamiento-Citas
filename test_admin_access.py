#!/usr/bin/env python
"""
Script de prueba para verificar el acceso al admin después de las correcciones de middleware.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

def test_admin_access():
    """
    Prueba el acceso al panel de administración con un superusuario.
    """
    print("🔧 Iniciando pruebas de acceso al admin...")
    
    # Crear cliente de prueba
    client = Client()
    
    try:
        # Obtener o crear superusuario
        superuser, created = User.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            superuser.set_password('admin123456')
            superuser.save()
            print("✅ Superusuario de prueba creado")
        else:
            print("✅ Usando superusuario existente")
        
        # Hacer login
        login_success = client.login(username='admin_test', password='admin123456')
        if login_success:
            print("✅ Login exitoso")
        else:
            print("❌ Error en login")
            return False
        
        # Probar acceso al admin principal
        response = client.get('/admin/')
        if response.status_code == 200:
            print("✅ Acceso al admin principal exitoso (200)")
        else:
            print(f"❌ Error acceso admin principal: {response.status_code}")
            return False
        
        # Probar acceso a una sección específica del admin
        response = client.get('/admin/auth/user/')
        if response.status_code == 200:
            print("✅ Acceso a admin/auth/user/ exitoso (200)")
        else:
            print(f"❌ Error acceso admin usuarios: {response.status_code}")
            return False
        
        # Probar acceso al sistema principal
        response = client.get('/')
        if response.status_code == 200:
            print("✅ Acceso al sistema principal exitoso (200)")
        else:
            print(f"❌ Error acceso sistema principal: {response.status_code}")
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✨ El acceso al admin está funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        return False
    
    finally:
        # Limpiar: eliminar usuario de prueba
        try:
            if User.objects.filter(username='admin_test').exists():
                User.objects.filter(username='admin_test').delete()
                print("🧹 Usuario de prueba eliminado")
        except Exception:
            pass

def check_middleware_configuration():
    """
    Verifica la configuración del middleware.
    """
    print("\n🔍 Verificando configuración de middleware...")
    
    from django.conf import settings
    
    middleware_list = settings.MIDDLEWARE
    security_middleware = 'agendamiento.middleware.SessionSecurityMiddleware'
    integrity_middleware = 'agendamiento.middleware.SessionIntegrityMiddleware'
    
    if security_middleware in middleware_list:
        print("✅ SessionSecurityMiddleware configurado")
    else:
        print("❌ SessionSecurityMiddleware NO configurado")
    
    if integrity_middleware in middleware_list:
        print("✅ SessionIntegrityMiddleware configurado")
    else:
        print("❌ SessionIntegrityMiddleware NO configurado")
    
    # Verificar orden
    auth_index = middleware_list.index('django.contrib.auth.middleware.AuthenticationMiddleware')
    try:
        security_index = middleware_list.index(security_middleware)
        integrity_index = middleware_list.index(integrity_middleware)
        
        if security_index > auth_index and integrity_index > auth_index:
            print("✅ Middleware personalizado correctamente posicionado después de AuthenticationMiddleware")
        else:
            print("⚠️  Advertencia: Middleware personalizado debería estar después de AuthenticationMiddleware")
    except ValueError:
        print("❌ Error: Middleware personalizado no encontrado en la configuración")

if __name__ == '__main__':
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    check_middleware_configuration()
    
    print("\n" + "=" * 50)
    success = test_admin_access()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 RESULTADO: ¡CORRECCIÓN EXITOSA!")
        print("📋 El problema de acceso al admin ha sido resuelto.")
        print("🔐 Los superusuarios ahora pueden acceder tanto al sistema principal como al admin.")
    else:
        print("🚨 RESULTADO: Aún hay problemas pendientes.")
        print("📋 Se requiere investigación adicional.")
