// App main JavaScript file

document.addEventListener('DOMContentLoaded', () => {
    // Initialize any components
    initModals();
    // Add animations
    initAnimations();
});

function initModals() {
    // Handle modal transitions
    const registerLink = document.querySelector('[data-bs-target="#registerModal"]');
    const loginLink = document.querySelector('[data-bs-target="#loginModal"]');

    if (registerLink) {
        registerLink.addEventListener('click', (e) => {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const bootstrapModal = bootstrap.Modal.getInstance(activeModal);
                bootstrapModal.hide();
            }
        });
    }

    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const bootstrapModal = bootstrap.Modal.getInstance(activeModal);
                bootstrapModal.hide();
            }
        });
    }
}

function initAnimations() {
    // Add scroll animations
    const serviceCards = document.querySelectorAll('.service-card');
    const professionalCards = document.querySelectorAll('.professional-card');

    // Simple animation on scroll for service cards
    if (serviceCards.length > 0) {
        window.addEventListener('scroll', () => {
            serviceCards.forEach(card => {
                const cardPosition = card.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;

                if (cardPosition < screenPosition) {
                    card.style.opacity = 1;
                    card.style.transform = 'translateY(0)';
                } else {
                    card.style.opacity = 0;
                    card.style.transform = 'translateY(20px)';
                }
            });
        });

        // Trigger once on load
        window.dispatchEvent(new Event('scroll'));
    }

    // Simple animation for professional cards
    if (professionalCards.length > 0) {
        window.addEventListener('scroll', () => {
            professionalCards.forEach(card => {
                const cardPosition = card.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;

                if (cardPosition < screenPosition) {
                    card.style.opacity = 1;
                    card.style.transform = 'translateY(0)';
                } else {
                    card.style.opacity = 0;
                    card.style.transform = 'translateY(20px)';
                }
            });
        });

        // Trigger once on load
        window.dispatchEvent(new Event('scroll'));
    }
}

// Mock demo function to simulate user location permission
function requestLocationPermission() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                },
                error => {
                    reject(error);
                }
            );
        } else {
            reject(new Error("Geolocation is not supported by this browser."));
        }
    });
}

