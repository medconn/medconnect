document.addEventListener('DOMContentLoaded', function () {
    initMaps();
    initAvailabilityToggle();
    setupMobileNav();
    initRequestInteractions();
});

// Inicializar mapas
function initMaps() {
    // Mapa de cobertura
    const coverageMap = L.map('coverage-map').setView([-33.45, -70.67], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(coverageMap);

    // Crear marcador para la ubicación del profesional
    const professionalIcon = L.divIcon({
        className: 'professional-marker',
        html: '<div class="marker-icon"><i class="fas fa-user-md"></i></div>',
        iconSize: [40, 40],
        iconAnchor: [20, 40]
    });

    // Agregar marcador del profesional
    const professionalMarker = L.marker([-33.45, -70.67], { icon: professionalIcon }).addTo(coverageMap);

    // Crear círculo de cobertura
    const coverageCircle = L.circle([-33.45, -70.67], {
        color: '#3a86ff',
        fillColor: '#3a86ff',
        fillOpacity: 0.1,
        radius: 10000
    }).addTo(coverageMap);

    // Controles de zoom
    document.getElementById('zoomIn').addEventListener('click', function () {
        coverageMap.zoomIn();
    });

    document.getElementById('zoomOut').addEventListener('click', function () {
        coverageMap.zoomOut();
    });

    // Mapa de servicio activo (si existe)
    const serviceMapElement = document.getElementById('service-map');
    if (serviceMapElement) {
        const serviceMap = L.map('service-map').setView([-33.44, -70.65], 14);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(serviceMap);

        // Marcador del profesional
        L.marker([-33.45, -70.67], { icon: professionalIcon }).addTo(serviceMap);

        // Marcador del paciente
        const patientIcon = L.divIcon({
            className: 'patient-marker',
            html: '<div class="marker-icon patient"><i class="fas fa-home"></i></div>',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        });

        L.marker([-33.44, -70.65], { icon: patientIcon }).addTo(serviceMap);

        // Línea de ruta
        const routePoints = [
            [-33.45, -70.67],
            [-33.445, -70.66],
            [-33.44, -70.65]
        ];

        const routeLine = L.polyline(routePoints, {
            color: '#3a86ff',
            weight: 4,
            opacity: 0.7,
            dashArray: '10, 10'
        }).addTo(serviceMap);

        // Ajustar vista para mostrar toda la ruta
        serviceMap.fitBounds(routeLine.getBounds(), {
            padding: [30, 30]
        });
    }
}

// Control de disponibilidad
function initAvailabilityToggle() {
    const availabilityToggle = document.getElementById('availabilityToggle');
    const statusText = document.getElementById('statusText');

    if (availabilityToggle && statusText) {
        availabilityToggle.addEventListener('change', function () {
            if (this.checked) {
                statusText.textContent = 'Disponible';
                statusText.classList.remove('bg-danger');
                statusText.classList.add('bg-success');
            } else {
                statusText.textContent = 'No Disponible';
                statusText.classList.remove('bg-success');
                statusText.classList.add('bg-danger');
            }
        });
    }
}

// Navegación móvil
function setupMobileNav() {
    const navItems = document.querySelectorAll('.mobile-nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // Eliminar clase activa de todos los elementos
            navItems.forEach(navItem => {
                navItem.classList.remove('active');
            });

            // Agregar clase activa al elemento seleccionado
            this.classList.add('active');

            // Si no es el enlace de inicio, prevenir navegación por defecto
            if (this.id !== 'pro-nav-home') {
                e.preventDefault();

                // Aquí se podría implementar navegación por SPA
                // Por ahora solo para demostración
                const targetSection = this.id.replace('pro-nav-', '');
                console.log(`Navegando a sección: ${targetSection}`);
            }
        });
    });
}

// Interacciones con solicitudes
function initRequestInteractions() {
    // Botones de aceptar/rechazar solicitud
    const acceptButtons = document.querySelectorAll('.request-card .btn-success');
    const rejectButtons = document.querySelectorAll('.request-card .btn-danger');

    acceptButtons.forEach(button => {
        button.addEventListener('click', function () {
            const requestCard = this.closest('.request-card');
            requestCard.classList.remove('new');
            requestCard.style.borderLeftColor = '#2ecc71';
            const badge = requestCard.querySelector('.request-badge span');
            if (badge) {
                badge.textContent = 'Aceptado';
                badge.classList.remove('bg-warning');
                badge.classList.add('bg-success');
            }

            // Mostrar mensaje de confirmación
            showNotification('Solicitud aceptada correctamente');
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function () {
            const requestCard = this.closest('.request-card');
            requestCard.classList.remove('new');
            requestCard.style.borderLeftColor = '#e74c3c';
            const badge = requestCard.querySelector('.request-badge span');
            if (badge) {
                badge.textContent = 'Rechazado';
                badge.classList.remove('bg-warning');
                badge.classList.add('bg-danger');
            }

            // Mostrar mensaje de confirmación
            showNotification('Solicitud rechazada');

            // Animar desaparición de la tarjeta
            setTimeout(() => {
                requestCard.style.opacity = '0';
                requestCard.style.height = '0';
                requestCard.style.margin = '0';
                requestCard.style.padding = '0';
                requestCard.style.overflow = 'hidden';
            }, 1000);
        });
    });
}

// Función para mostrar notificaciones
function showNotification(message) {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = 'toast-notification';
    notification.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-check-circle"></i>
        </div>
        <div class="toast-content">${message}</div>
    `;

    // Agregar al DOM
    document.body.appendChild(notification);

    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Ocultar después de un tiempo
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

