# Sistema de Agendamiento de Citas Médicas v2.0 - IPS Medical Integral

Sistema de gestión de citas médicas modernas, optimizado para clínicas de nivel I y II.
Desarrollado con **Django 5** y arquitectura en la nube.

---

## 🚀 Estado del Proyecto
![Status](https://img.shields.io/badge/Estado-Producción-green)
![Version](https://img.shields.io/badge/Versión-2.0-blue)
![DB](https://img.shields.io/badge/DB-Neon_Serverless-purple)

## 📋 Resumen Ejecutivo
Plataforma web integral para la automatización del proceso de agendamiento de citas médicas. Soluciona la problemática de gestión manual, solapamiento de horarios y falta de centralización de la información del paciente.

**Características Principales:**
*   **Gestión de Roles:** Módulos independientes para Pacientes, Profesionales y Asesores.
*   **Agendamiento Inteligente:** Validación en tiempo real de disponibilidad y conflictos.
*   **Infraestructura Híbrida:** Desarrollo ágil en SQLite y Producción robusta en Neon (PostgreSQL Serverless).

## 🛠 Stack Tecnológico de Nueva Generación

### Backend & Core
*   **Framework:** Python 3.12 + Django 5.0.14
*   **Base de Datos (Producción):** Neon Serverless Postgres (Escalabilidad automática).
*   **Seguridad:** Middleware personalizado para sesiones y protección CSRF/XSS.

### Frontend (En Transición)
*   **Actual:** HTML5 / CSS3 / Vanilla JS.
*   **Roadmap v2.1:** Migración en curso a **Bootstrap 5 Premium**.

### Infraestructura
*   **Despliegue:** Render PaaS.
*   **Servidor:** Gunicorn + WhiteNoise (Archivos estáticos).

---

## ⚙️ Reglas de Negocio Críticas (Actualizado v2.0)

El sistema implementa validaciones estrictas para garantizar la integridad de la agenda médica:

### 1. Validación de Solapamiento (Paciente) - *Nuevo*
Para evitar que un paciente se agende en múltiples especialidades simultáneamente:
*   **Regla:** Un paciente no puede tener dos citas que se solapen en tiempo.
*   **Buffer de Seguridad:** Se exige obligatoriamente un **margen de 10 minutos** entre la finalización de una cita y el inicio de la siguiente (tiempo de desplazamiento dentro de la clínica).

### 2. Validación Temporal
*   **Prohibición de Pasado:** El sistema rechaza automáticamente cualquier intento de agendar citas en fechas u horas anteriores al momento actual del servidor.
*   **Horario Laboral:** Restricción automática para agendar solo dentro de los bloques definidos en las plantillas del médico.

---

## 🏗 Arquitectura del Sistema

```mermaid
graph TD
    User((Usuario))
    LB[Load Balancer]
    Guni[Gunicorn WSGI]
    Django[Django App]
    Neon[(Neon Postgres DB)]
    
    User -->|HTTPS| LB
    LB --> Guni
    Guni --> Django
    Django -->|ORM| Neon
    Django -->|Auth/Logic| Django
```

---

## 🚀 Guía de Instalación (Desarrolladores)

### Prerrequisitos
*   Python 3.12+
*   Cuenta en Neon.tech (para BD producción)

### Pasos
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/kevinagredojara/Sistema-Agendamiento-Citas.git
    cd Sistema-Agendamiento-Citas
    ```

2.  **Configurar Entorno:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```

3.  **Variables de Entorno (`.env`):**
    ```env
    DEBUG=True
    SECRET_KEY=tu_clave_secreta
    DATABASE_URL=postgres://user:pass@ep-neondb.region.aws.neon.tech/dbname
    ```

4.  **Ejecutar:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## 🧪 Testing

El proyecto cuenta con una suite de pruebas robusta que valida las reglas de negocio críticas.

**Ejecutar suite completa:**
```bash
python manage.py test agendamiento
```

**Verificar corrección de solapamiento (Caso Paola):**
```bash
python test_patient_overlap.py # (Script de verificación manual)
```

---

*© 2025 IPS Medical Integral Solutions.*
