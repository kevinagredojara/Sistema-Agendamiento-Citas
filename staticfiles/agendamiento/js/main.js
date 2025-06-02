// JavaScript principal para Medical Integral
document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar funcionalidades básicas
    initializeComponents();
    
    // Auto-ocultar mensajes después de 5 segundos
    autoHideMessages();
    
});

// Inicializar componentes básicos
function initializeComponents() {
    console.log('Medical Integral - Sistema de Citas cargado');
    
    // Aquí agregaremos más funcionalidades según las necesitemos
}

// Auto-ocultar mensajes del sistema
function autoHideMessages() {
    const messages = document.querySelectorAll('.message');
    
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000); // 5 segundos
    });
}

// Confirmar acciones peligrosas (como eliminar)
function confirmAction(message) {
    return confirm(message || '¿Estás seguro de que deseas realizar esta acción?');
}

// Función para manejar formularios con confirmación
function setupFormConfirmations() {
    const dangerousForms = document.querySelectorAll('form[data-confirm]');
    
    dangerousForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const message = form.getAttribute('data-confirm');
            if (!confirmAction(message)) {
                e.preventDefault();
            }
        });
    });
}

// Llamar la función de confirmaciones
setupFormConfirmations();
