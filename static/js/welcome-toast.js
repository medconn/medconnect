/**
 * Welcome Toast - Mensaje de bienvenida para usuarios que acaban de iniciar sesión
 * MedConnect - Sistema de gestión médica
 */

// Variable global para prevenir múltiples inicializaciones
if (typeof window.medConnectWelcomeToastInitialized === 'undefined') {
    window.medConnectWelcomeToastInitialized = false;
}

document.addEventListener('DOMContentLoaded', function () {
    // Prevenir múltiples inicializaciones
    if (window.medConnectWelcomeToastInitialized) {
        console.warn('⚠️ Welcome toast ya está inicializado, saltando...');
        return;
    }

    // Verificar si hay elementos duplicados
    const welcomeToasts = document.querySelectorAll('#welcomeToast');
    if (welcomeToasts.length > 1) {
        console.error(`❌ Se encontraron ${welcomeToasts.length} elementos con id "welcomeToast", removiendo duplicados...`);
        // Remover todos excepto el primero
        for (let i = 1; i < welcomeToasts.length; i++) {
            welcomeToasts[i].remove();
        }
    }

    const welcomeToast = document.getElementById('welcomeToast');

    if (welcomeToast) {
        // Marcar como inicializado
        window.medConnectWelcomeToastInitialized = true;

        // Verificar si ya se procesó antes
        if (welcomeToast.dataset.processed === 'true') {
            console.warn('⚠️ Welcome toast ya fue procesado, saltando...');
            return;
        }

        // Marcar como procesado
        welcomeToast.dataset.processed = 'true';

        console.log('🎉 Inicializando welcome toast...');

        // Agregar animación de salida si no existe
        if (!document.querySelector('#welcome-toast-styles')) {
            const style = document.createElement('style');
            style.id = 'welcome-toast-styles';
            style.textContent = `
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
                
                .welcome-toast-fade-out {
                    animation: slideOutRight 0.5s ease-in forwards;
                }
            `;
            document.head.appendChild(style);
        }

        // Función para ocultar el toast
        function hideWelcomeToast() {
            if (welcomeToast.style.display === 'none') {
                return; // Ya está oculto
            }

            welcomeToast.classList.add('welcome-toast-fade-out');
            setTimeout(function () {
                welcomeToast.style.display = 'none';
                console.log('✅ Welcome toast ocultado');
            }, 500);
        }

        // Auto-ocultar después de 5 segundos
        const autoHideTimer = setTimeout(hideWelcomeToast, 5000);

        // Permitir cerrar manualmente si se hace clic
        welcomeToast.addEventListener('click', function () {
            clearTimeout(autoHideTimer); // Cancelar timer automático
            hideWelcomeToast();
        });

        // Agregar un pequeño botón de cerrar si no existe
        if (!welcomeToast.querySelector('.btn-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.className = 'btn-close position-absolute top-0 end-0 m-2';
            closeBtn.style.fontSize = '1.2rem';
            closeBtn.style.background = 'none';
            closeBtn.style.border = 'none';
            closeBtn.style.color = 'rgba(255,255,255,0.8)';
            closeBtn.style.cursor = 'pointer';
            closeBtn.style.zIndex = '10000';
            closeBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                clearTimeout(autoHideTimer); // Cancelar timer automático
                hideWelcomeToast();
            });

            welcomeToast.appendChild(closeBtn);
        }

        console.log('✅ Welcome toast inicializado correctamente');
    } else {
        console.log('ℹ️ No se encontró elemento welcomeToast en esta página');
    }
}); 