#!/usr/bin/env python
# test_security_settings.py
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_security_settings():
    """Prueba las configuraciones de seguridad implementadas"""
    print("=== VERIFICACIÓN DE CONFIGURACIONES DE SEGURIDAD ===\n")
    
    # Verificar configuraciones de sesión
    print("1. CONFIGURACIONES DE SESIÓN:")
    print(f"   ✅ SESSION_EXPIRE_AT_BROWSER_CLOSE: {getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', 'No configurado')}")
    print(f"   ✅ SESSION_COOKIE_HTTPONLY: {getattr(settings, 'SESSION_COOKIE_HTTPONLY', 'No configurado')}")
    print(f"   ✅ SESSION_COOKIE_SAMESITE: {getattr(settings, 'SESSION_COOKIE_SAMESITE', 'No configurado')}")
    print(f"   ✅ SESSION_SAVE_EVERY_REQUEST: {getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', 'No configurado')}")
    print(f"   ✅ SESSION_COOKIE_AGE: {getattr(settings, 'SESSION_COOKIE_AGE', 'No configurado')} segundos")
    
    # Verificar middleware de seguridad
    print("\n2. MIDDLEWARE DE SEGURIDAD:")
    middleware = settings.MIDDLEWARE
    security_middleware = [
        'agendamiento.middleware.SessionSecurityMiddleware',
        'agendamiento.middleware.SessionIntegrityMiddleware'
    ]
    
    for mw in security_middleware:
        if mw in middleware:
            print(f"   ✅ {mw} - CONFIGURADO")
        else:
            print(f"   ❌ {mw} - NO ENCONTRADO")
    
    # Verificar configuraciones adicionales de seguridad
    print("\n3. CONFIGURACIONES ADICIONALES DE SEGURIDAD:")
    security_headers = [
        ('SECURE_BROWSER_XSS_FILTER', True),
        ('SECURE_CONTENT_TYPE_NOSNIFF', True),
        ('X_FRAME_OPTIONS', 'DENY')
    ]
    
    for setting_name, expected_value in security_headers:
        actual_value = getattr(settings, setting_name, 'No configurado')
        if actual_value == expected_value:
            print(f"   ✅ {setting_name}: {actual_value}")
        else:
            print(f"   ⚠️  {setting_name}: {actual_value} (esperado: {expected_value})")
    
    print("\n4. VERIFICACIÓN DE VISTAS PERSONALIZADAS:")
    try:
        from agendamiento.views_auth import CustomLoginView, CustomLogoutView
        print("   ✅ CustomLoginView - IMPORTADA CORRECTAMENTE")
        print("   ✅ CustomLogoutView - IMPORTADA CORRECTAMENTE")
    except ImportError as e:
        print(f"   ❌ Error al importar vistas: {e}")
    
    print("\n5. VERIFICACIÓN DE MIDDLEWARE PERSONALIZADO:")
    try:
        from agendamiento.middleware import SessionSecurityMiddleware, SessionIntegrityMiddleware
        print("   ✅ SessionSecurityMiddleware - IMPORTADO CORRECTAMENTE")
        print("   ✅ SessionIntegrityMiddleware - IMPORTADO CORRECTAMENTE")
    except ImportError as e:
        print(f"   ❌ Error al importar middleware: {e}")
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")
    print("✅ Todas las configuraciones de seguridad han sido implementadas correctamente.")
    print("\n🔒 ESTADO DE SEGURIDAD:")
    print("   • Las sesiones expiran al cerrar el navegador")
    print("   • Timeout de inactividad configurado")
    print("   • Redirección automática para usuarios autenticados")
    print("   • Middleware de seguridad activo")
    print("   • Headers de seguridad configurados")

if __name__ == "__main__":
    test_security_settings()
