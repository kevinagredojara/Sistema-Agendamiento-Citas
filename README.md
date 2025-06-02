# Sistema-Agendamiento-Citas
Producto Mínimo Viable de un Sistema de Agendamiento de Citas Médicas para la IPS Medical Integral. Proyecto de Grado

## Configuración del Entorno de Desarrollo

### Variables de Entorno
Este proyecto utiliza variables de entorno para mantener la seguridad de credenciales sensibles.

**Configuración inicial:**
1. Copia el archivo de ejemplo: `cp .env.example .env`
2. Genera una nueva SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
3. Actualiza el archivo `.env` con tu clave generada
4. Instala dependencias: `pip install python-dotenv`

**Nota:** El archivo `.env` está protegido en `.gitignore` y nunca debe ser versionado.

Para más detalles, consulta: `CONFIGURACION_VARIABLES_ENTORNO.md`
