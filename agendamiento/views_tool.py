
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Paciente, ProfesionalSalud, Cita, AsesorServicio, PlantillaHorarioMedico

def emergency_reset_view(request):
    """
    Vista temporal para reiniciar usuarios y crear superadmin en producción.
    Solo accesible con clave secreta en URL.
    """
    # Simple mecanismo de seguridad
    if request.GET.get('key') != 'RellenoSanitario2026':
        return HttpResponse("<h1>Acceso Denegado</h1>", status=403)

    log = []
    
    try:
        with transaction.atomic():
            # 1. Limpieza de datos (Orden importante por claves foráneas)
            # Primero citas y horarios
            deleted_citas, _ = Cita.objects.all().delete()
            log.append(f"Citas eliminadas: {deleted_citas}")
            
            deleted_horarios, _ = PlantillaHorarioMedico.objects.all().delete()
            log.append(f"Plantillas Horario eliminadas: {deleted_horarios}")

            # Perfiles
            Paciente.objects.all().delete()
            ProfesionalSalud.objects.all().delete()
            AsesorServicio.objects.all().delete()
            log.append("Perfiles eliminados.")

            # Usuarios
            User = get_user_model()
            users_count, _ = User.objects.all().delete()
            log.append(f"Usuarios eliminados: {users_count}")

            # 2. Creación de Superusuario
            username = 'admin_web'
            email = 'admin@web.com'
            password = 'AdminWeb2026!'
            
            User.objects.create_superuser(username, email, password)
            log.append(f"<b>CREADO SUPERUSUARIO:</b> {username} / {password}")

    except Exception as e:
        return HttpResponse(f"<h1>Error Crítico:</h1><pre>{str(e)}</pre>")

    return HttpResponse(f"<h1>Operación Exitosa</h1><br>" + "<br>".join(log) + f"<br><br><a href='/agendamiento/login/'>IR AL LOGIN</a>")
