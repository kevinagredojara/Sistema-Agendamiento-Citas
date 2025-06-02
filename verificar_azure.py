#!/usr/bin/env python
"""
Script de Verificación Pre-Despliegue Azure
Sistema de Agendamiento de Citas
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

def verificar_configuracion_azure():
    """Verificar configuraciones básicas para Azure"""
    print("🔧 VERIFICANDO CONFIGURACIÓN AZURE...")
    
    # Importar configuraciones Azure
    try:
        from azure_settings import REQUIRED_ENV_VARS, OPTIONAL_ENV_VARS
        print("✅ Archivo azure_settings.py encontrado")
    except ImportError:
        print("❌ Error: No se pudo importar azure_settings.py")
        return False
    
    # Verificar variables críticas
    missing_critical = []
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            missing_critical.append(var)
    
    if missing_critical:
        print(f"⚠️  Variables críticas faltantes: {missing_critical}")
        print("   (Esto es normal en desarrollo local)")
    else:
        print("✅ Todas las variables críticas configuradas")
    
    return True

def ejecutar_tests_azure():
    """Ejecutar solo los tests críticos de Azure"""
    print("\n🧪 EJECUTANDO TESTS CRÍTICOS AZURE...")
    
    # Configurar Django para testing
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Ejecutar tests específicos de Azure
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1)
    
    test_classes = [
        'agendamiento.tests.TestConfiguracionAzure',
        'agendamiento.tests.TestConexionBaseDatos', 
        'agendamiento.tests.TestCSRFProtection'
    ]
    
    failures = test_runner.run_tests(test_classes)
    
    if failures:
        print(f"❌ {failures} tests fallaron")
        return False
    else:
        print("✅ Todos los tests Azure pasaron exitosamente")
        return True

def verificar_archivos_requeridos():
    """Verificar que todos los archivos necesarios existen"""
    print("\n📁 VERIFICANDO ARCHIVOS REQUERIDOS...")
    
    archivos_requeridos = [
        'azure_settings.py',
        'agendamiento/tests.py',
        'manage.py',
        'core_project/settings.py'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"❌ Archivos faltantes: {archivos_faltantes}")
        return False
    else:
        print("✅ Todos los archivos requeridos presentes")
        return True

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("🚀 VERIFICACIÓN PRE-DESPLIEGUE AZURE")
    print("   Sistema de Agendamiento de Citas")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    if os.path.basename(os.getcwd()) != 'Sistema-Agendamiento-Citas':
        if os.path.exists('Sistema-Agendamiento-Citas'):
            os.chdir('Sistema-Agendamiento-Citas')
        else:
            print("❌ Error: No se encuentra el directorio del proyecto")
            return False
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(verificar_archivos_requeridos())
    resultados.append(verificar_configuracion_azure())
    resultados.append(ejecutar_tests_azure())
    
    # Mostrar resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if all(resultados):
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ El sistema está listo para despliegue en Azure")
        print("\n📋 Próximos pasos:")
        print("   1. Configurar variables de entorno en Azure App Service")
        print("   2. Configurar base de datos Azure")
        print("   3. Ejecutar despliegue")
        print("   4. Ejecutar tests en producción")
        return True
    else:
        print("⚠️  VERIFICACIÓN CON ADVERTENCIAS")
        print("   Revisar los elementos marcados arriba")
        print("   El sistema puede funcionar pero se recomienda revisión")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
