# Informe Técnico Detallado
## Sistema de Agendamiento de Citas Médicas - IPS Medical Integral

**Proyecto:** Sistema Web de Agendamiento de Citas  
**Desarrollador:** Kevin Agredo Jara | Ficha 2977355  
**Instructor:** Nain Zuñiga Porto | SENA  
**Fecha:** Octubre 2025

---

## Resumen

Este documento explica cómo funciona el **Sistema de Agendamiento de Citas Médicas** desarrollado para la IPS Medical Integral. Es una aplicación web completa que automatiza el proceso de agendar citas entre pacientes y profesionales de la salud.

### ¿Qué logramos con este proyecto?

- ✅ Aplicar el patrón MVT de Django en una app real
- ✅ Desarrollar backend y frontend completamente integrados
- ✅ Implementar seguridad (autenticación, permisos, validaciones)
- ✅ Crear 26 tests automatizados con 95% de cobertura
- ✅ Desplegar en la nube (Render) con deployment automático

---

## Contenido

1. [Fundamentos Técnicos](#1-fundamentos-técnicos)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Base de Datos](#3-base-de-datos)
4. [Funcionalidades Principales](#4-funcionalidades-principales)
5. [Seguridad](#5-seguridad)
6. [Interfaz de Usuario](#6-interfaz-de-usuario)
7. [Testing](#7-testing)
8. [Deployment](#8-deployment)
9. [Performance](#9-performance)
10. [Conclusiones](#10-conclusiones)

---

## 1. Fundamentos Técnicos

### 1.1 Tecnologías Elegidas

**¿Por qué Django?**
- Tiene el patrón MVT integrado (perfecto para aprender arquitecturas web)
- Trae autenticación, ORM y panel admin listos para usar
- Es seguro por defecto (protección contra XSS, CSRF, SQL injection)

**¿Por qué dos bases de datos?**
- **Desarrollo local:** SQLite (rápida, sin configuración)
- **Producción:** PostgreSQL (robusta, escalable, provista por Render)

```python
# Django cambia automáticamente según la variable DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}
```

### 1.2 Arquitectura MVT (Model-View-Template)

**Flujo simplificado:**

1. **Cliente** → Hace petición HTTP → **URLs** enrutan a la vista correcta
2. **Vista** → Consulta **Modelos** → Obtiene datos de la **Base de Datos**
3. **Vista** → Pasa datos al **Template** → Renderiza HTML
4. **Template** → Responde al **Cliente**

### 1.3 Stack Tecnológico

| Componente | Tecnología | Para qué sirve |
|------------|------------|----------------|
| **Backend** | Python 3.12 + Django 5.0.14 | Lógica del servidor, ORM, autenticación |
| **Base de Datos** | SQLite (dev) / PostgreSQL (prod) | Almacenar datos de pacientes, citas, etc. |
| **Frontend** | HTML5/CSS3/JavaScript | Interfaces de usuario responsivas |
| **Servidor** | Gunicorn + WhiteNoise | Servir la app en producción |
| **Hosting** | Render (PaaS) | Deployment automático desde GitHub |

---

## 2. Arquitectura del Sistema

### 2.1 Capas del Sistema

El sistema usa una arquitectura en 4 capas:

1. **Presentación:** Templates HTML + CSS + JavaScript (24 archivos)
2. **Aplicación:** Views (22 vistas) + Forms (7 formularios) + Decorators
3. **Negocio:** Models (5 modelos) + Validators + Middleware
4. **Datos:** Django ORM + Base de Datos + Migraciones

### 2.2 Organización por Roles

Las vistas están separadas por tipo de usuario:

```
agendamiento/
├── views_auth.py          # Login, logout, registro
├── views_paciente.py      # Dashboard y funciones de pacientes
├── views_profesional.py   # Agenda y gestión de citas
├── views_asesor.py        # Panel administrativo
└── views.py              # Vistas compartidas
```

**Ventajas:** Cada archivo es independiente, fácil de mantener, y se pueden agregar nuevos roles sin afectar el código existente.

### 2.3 Patrones de Diseño Usados

| Patrón | Implementación | Para qué sirve |
|--------|----------------|----------------|
| **Decorator** | `@paciente_required`, `@profesional_required` | Controlar acceso según rol del usuario |
| **Template Method** | `base.html` con bloques {% block %} | Reutilizar estructura HTML común |
| **Observer** | Middleware personalizado | Monitorear seguridad en cada petición |
| **Factory** | `forms.py` con ModelForm | Crear formularios automáticamente desde modelos |

---

## 3. Base de Datos

### 3.1 Modelos Principales

El sistema tiene 5 modelos principales:

**User (Django built-in)** → Autenticación base  
├─ **Paciente** (1:1) → Datos del paciente (documento, teléfono, fecha nacimiento)  
├─ **Profesional** (1:1) → Datos del médico (registro profesional, especialidad)  
└─ **Asesor** (1:1) → Personal administrativo

**Especialidad** → Catálogo (nombre, duración consulta)  
**Cita** → Relación entre Paciente + Profesional (fecha, hora, estado)  
**PlantillaHorario** → Horarios de atención por día de la semana

### 3.2 Relaciones Clave

```python
# Cada usuario tiene UN perfil
user.paciente_perfil  # Relación OneToOne

# Un profesional tiene MUCHAS citas
profesional.citas_asignadas.all()  # ForeignKey reverso

# Una cita pertenece a UN paciente y UN profesional
cita.paciente  # ForeignKey
cita.profesional  # ForeignKey
```

### 3.3 Validaciones Importantes

**A nivel de modelo:**
- Fechas de citas no pueden ser pasadas
- No se permiten documentos duplicados
- Los profesionales no pueden tener 2 citas a la misma hora

**A nivel de base de datos:**
- Constraints de unicidad (UNIQUE)
- Índices en campos frecuentes (fecha_cita, profesional, paciente)

### 3.4 Optimización de Consultas

Para evitar que la base de datos sea lenta, usamos:

**select_related()** → Cuando necesitamos datos relacionados (1 query en vez de N+1)
```python
# Malo (hace 100 queries si hay 100 citas)
citas = Cita.objects.all()
for cita in citas:
    print(cita.paciente.nombre)  # Query adicional cada vez

# Bueno (hace solo 1 query)
citas = Cita.objects.select_related('paciente', 'profesional')
```

**Índices en campos frecuentes:**
- `fecha_cita + profesional` (para buscar disponibilidad)
- `paciente + estado` (para ver citas del paciente)

---

## 4. Funcionalidades Principales

### 4.1 Control de Acceso por Roles

Usamos **decoradores** para proteger vistas según el rol del usuario:

```python
@paciente_required
def mis_citas(request):
    # Solo pacientes pueden entrar aquí
    paciente = request.user.paciente_perfil
    citas = paciente.citas.all()
    return render(request, 'mis_citas.html', {'citas': citas})
```

**¿Cómo funciona?**
1. Usuario intenta acceder a una vista
2. Decorador verifica si está autenticado
3. Verifica si tiene el perfil correcto (paciente, profesional, asesor)
4. Si no cumple → Redirige al login con mensaje de error

### 4.2 Middleware de Seguridad

Creamos un middleware personalizado que revisa **cada petición** antes de procesarla:

**Funciones:**
- Verificar integridad de la sesión
- Detectar actividad sospechosa (muchos parámetros GET, SQL en URLs)
- Registrar eventos de seguridad en logs

### 4.3 Cálculo de Disponibilidad

**Problema:** ¿Cómo saber qué horas están libres para un profesional en una fecha?

**Solución:**
1. Generar todos los slots posibles (8:00 AM - 5:00 PM cada 30 min)
2. Consultar citas ya agendadas del profesional ese día
3. Marcar como ocupados los slots con citas
4. Devolver lista de horarios disponibles

**Optimización:** Hacemos UNA sola query a la base de datos al inicio, no una por cada hora.

### 4.4 Validaciones en Formularios

Los formularios validan datos en múltiples niveles:

**Validaciones de campo individual:**
- Fecha no puede ser pasada
- Fecha no puede ser más de 6 meses en el futuro
- No se permite agendar domingos

**Validaciones cruzadas:**
- El profesional no puede tener otra cita a la misma hora
- El paciente no puede tener más de 2 citas el mismo día

**¿Por qué validar en el servidor?**
Aunque JavaScript valida en el navegador, siempre validamos en el servidor porque un usuario malicioso puede saltarse las validaciones del frontend.

---

## 5. Seguridad

### 5.1 Capas de Seguridad

Django protege el sistema en múltiples niveles:

**1. Frontend (Templates)**
- Escaping automático (previene XSS)
- CSRF tokens en todos los formularios

**2. Aplicación (Views)**
- Decoradores de control de acceso
- Validación de formularios en el servidor

**3. Middleware**
- Verificación de integridad de sesión
- Detección de actividad sospechosa

**4. Base de Datos**
- ORM previene SQL injection
- Constraints de unicidad

### 5.2 Configuración de Producción

**En desarrollo (DEBUG=True):**
- Errores detallados visibles
- Sin HTTPS obligatorio

**En producción (DEBUG=False):**
- `SECURE_SSL_REDIRECT = True` → Forzar HTTPS
- `SESSION_COOKIE_SECURE = True` → Cookies solo por HTTPS
- `X_FRAME_OPTIONS = 'DENY'` → Prevenir clickjacking
- Sesiones expiran en 1 hora

### 5.3 Validadores Personalizados

| Validador | Qué valida |
|-----------|------------|
| `validate_numero_documento` | Solo números, entre 6-12 dígitos |
| `validate_telefono_colombiano` | Formato +57 XXX XXX XXXX |
| `validate_hora_laboral` | Entre 8:00 AM y 5:00 PM |

### 5.4 Sistema de Logs

Los logs registran eventos importantes del sistema:

**general.log** → Operaciones normales (INFO)
**security.log** → Eventos de seguridad (WARNING, ERROR)

Cada entrada incluye: timestamp, nivel, proceso, mensaje

---

## 6. Interfaz de Usuario

### 6.1 Diseño Responsivo

**Mobile-first:** El sistema se adapta a cualquier tamaño de pantalla

**Breakpoints:**
- **Móvil:** < 768px (columnas al 100%)
- **Tablet:** 768-1024px (2 columnas)
- **Desktop:** > 1024px (3-4 columnas)

**Variables CSS para consistencia:**
```css
:root {
    --primary-color: #2c3e50;
    --success-color: #27ae60;
    --danger-color: #e74c3c;
    --border-radius: 8px;
}
```

### 6.2 Estructura de Templates

**base.html** → Template padre con:
- Header con navegación
- Sistema de mensajes (success, error, warning)
- Área de contenido ({% block content %})
- Footer

**Templates hijos** → Extienden base.html:
```html
{% extends 'agendamiento/base.html' %}
{% block content %}
    <!-- Contenido específico -->
{% endblock %}
```

### 6.3 JavaScript para Interactividad

**Funcionalidades clave:**
- Menú móvil responsive
- Validación de formularios en tiempo real
- Selector de fechas con restricciones (no domingos, no fechas pasadas)
- Carga de horarios disponibles vía AJAX
- Sistema de alertas automáticas

---

## 7. Testing

### 7.1 Suite de Tests

El sistema tiene **26 tests automatizados** que validan todas las funcionalidades críticas.

**Categorías de tests:**
- Validación de modelos (unicidad, fechas, constraints)
- Autenticación y roles (redirecciones, permisos)
- Agendamiento de citas (disponibilidad, conflictos)
- Seguridad (CSRF, SQL injection, control de acceso)

### 7.2 Cobertura de Código

**Resultados:**
- **Cobertura total:** 95%
- **models.py:** 96%
- **views_*.py:** 95-97%
- **forms.py:** 97%
- **validators.py:** 97%

**Comando para verificar:**
```bash
coverage run --source='.' manage.py test
coverage report -m
```

### 7.3 Ejemplos de Tests Críticos

**Test de conflicto de horarios:**
Verifica que no se puedan crear 2 citas a la misma hora para el mismo profesional.

**Test de control de acceso:**
Un paciente no puede acceder al dashboard de profesionales (y viceversa).

**Test de performance:**
El listado de citas debe cargar en menos de 2 segundos usando `select_related()`.

---

## 8. Deployment

### 8.1 Plataforma: Render

**¿Por qué Render?**
- Deployment automático desde GitHub
- PostgreSQL incluido
- HTTPS automático
- Free tier para proyectos académicos

### 8.2 Archivos de Configuración

**Procfile** → Define cómo iniciar la app:
```
web: gunicorn core_project.wsgi --log-file -
```

**startup.sh** → Script de inicialización:
```bash
#!/bin/bash
python manage.py migrate           # Aplicar migraciones
python manage.py collectstatic --noinput  # Recolectar archivos estáticos
python manage.py create_initial_superuser  # Crear admin
exec gunicorn core_project.wsgi
```

### 8.3 Variables de Entorno

**Configuradas en Render:**
- `DATABASE_URL` → Conexión PostgreSQL (automática)
- `SECRET_KEY` → Clave secreta Django
- `ALLOWED_HOSTS` → Dominio de Render
- `DEBUG=False` → Modo producción

### 8.4 Diferencias Desarrollo vs Producción

| Aspecto | Desarrollo | Producción |
|---------|------------|------------|
| Base de Datos | SQLite | PostgreSQL |
| DEBUG | True | False |
| HTTPS | Opcional | Obligatorio |
| Archivos estáticos | Django sirve directamente | WhiteNoise optimizado |
| Logs | Console detallado | Archivo rotativo |

---

## 9. Performance

### 9.1 Optimizaciones Implementadas

**Queries optimizadas:**
- `select_related()` para relaciones OneToOne y ForeignKey
- `prefetch_related()` para relaciones ManyToMany
- `only()` cuando solo necesitamos campos específicos

**Caching (futuro):**
- Disponibilidad de horarios (cache de 5 minutos)
- Datos de especialidades (cambianpoco)
- Sesiones en Redis para escalamiento horizontal

**Índices de base de datos:**
- Fecha + Profesional (búsquedas de disponibilidad)
- Paciente + Estado (historial del paciente)

### 9.2 Métricas de Rendimiento

**Benchmarks actuales:**
- Listado de citas: < 2 segundos
- Cálculo de disponibilidad: < 0.5 segundos
- Dashboard: < 1.5 segundos

**Optimizaciones futuras:**
- CDN para archivos estáticos
- Redis para caché distribuido
- Celery para tareas asíncronas (emails, notificaciones)

### 9.3 Escalabilidad

**Vertical (escalar hardware):**
- Aumentar CPU/RAM del servidor Render
- Escalar PostgreSQL a plan superior

**Horizontal (más instancias):**
- Múltiples workers de Gunicorn
- Balance de carga automático (Render)
- Sesiones en Redis (stateless)

---

## 10. Conclusiones

### 10.1 Objetivos Logrados

✅ **Aplicar patrones de diseño:** MVT, Decorator, Factory, Template Method  
✅ **Desarrollo Full-Stack:** Backend Django + Frontend HTML/CSS/JS  
✅ **Seguridad robusta:** Autenticación, autorización, validaciones, middleware  
✅ **Testing completo:** 26 tests con 95% de cobertura  
✅ **Deployment exitoso:** Render con despliegue automático

### 10.2 Competencias Desarrolladas

**Técnicas:**
- Dominio de Django (ORM, templates, forms, middleware)
- Diseño de base de datos relacionales
- Seguridad en aplicaciones web
- Testing automatizado

**Metodológicas:**
- Git y control de versiones
- Deployment y DevOps
- Documentación técnica
- Resolución de problemas

### 10.3 Desafíos Superados

**1. Concurrencia en agendamiento**
- Problema: Múltiples usuarios agendando la misma hora
- Solución: Constraints de base de datos + validación en forms

**2. Optimización de performance**
- Problema: Queries N+1 en listados
- Solución: select_related() y prefetch_related()

**3. Control de acceso multi-rol**
- Problema: 3 tipos de usuario con permisos diferentes
- Solución: Decoradores personalizados por rol

### 10.4 Trabajo Futuro

**Corto plazo (1-3 meses):**
- Notificaciones por email/SMS
- Exportar historial de citas a PDF
- Dashboard con gráficos estadísticos

**Mediano plazo (3-6 meses):**
- Historia clínica digital básica
- Integración con pasarelas de pago
- App móvil (React Native o Flutter)

**Largo plazo (6-12 meses):**
- Telemedicina (videollamadas)
- IA para predicción de no-shows
- API REST pública para integraciones

### 10.5 Impacto del Proyecto

Este proyecto demuestra la capacidad de:
- Desarrollar sistemas reales con tecnologías modernas
- Aplicar buenas prácticas de ingeniería de software
- Trabajar con plataformas cloud
- Resolver problemas complejos del mundo real

El sistema está **listo para producción** y puede escalarse para hospitales o clínicas de mayor tamaño.

---

## Anexos

### A. Stack Tecnológico Final

```
Backend:  Python 3.12 + Django 5.0.14
Frontend: HTML5 + CSS3 + JavaScript (Vanilla)
BD Dev:   SQLite 3
BD Prod:  PostgreSQL 14+
Server:   Gunicorn 23.0.0
Static:   WhiteNoise 6.9.0
Host:     Render (PaaS)
Repo:     GitHub
```

### B. Comandos Útiles

```bash
# Desarrollo local
python manage.py runserver
python manage.py makemigrations
python manage.py migrate

# Testing
python manage.py test
coverage run --source='.' manage.py test
coverage report -m

# Producción
python manage.py collectstatic
python manage.py check --deploy
gunicorn core_project.wsgi
```

### C. Estructura de Archivos Clave

```
core_project/settings.py  → Configuración Django
agendamiento/models.py    → Modelos de datos
agendamiento/views_*.py   → Lógica de negocio
agendamiento/forms.py     → Validación formularios
agendamiento/tests.py     → Suite de tests
Procfile                  → Comando para Render
startup.sh                → Script de inicialización
requirements.txt          → Dependencias Python
```

---

**Documento elaborado por:** Kevin Agredo Jara  
**Fecha:** Octubre 2025  
**Versión:** 2.0 
