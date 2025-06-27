// MedConnect - Patient Dashboard JavaScript
// Diseño simple y funcional con carga dinámica de datos

// Variables globales
let currentUserId = null;

// Funciones principales
function scheduleAppointment() {
    showNotification('📅 Redirigiendo al ChatBot para agendar cita...', 'info');
    setTimeout(() => {
        window.open('https://t.me/Medconn_bot', '_blank');
    }, 1000);
}

function addMedication() {
    showNotification('💊 Redirigiendo al ChatBot para agregar medicamento...', 'info');
    setTimeout(() => {
        window.open('https://t.me/Medconn_bot', '_blank');
    }, 1000);
}

function addExam() {
    showNotification('🩺 Redirigiendo al ChatBot para registrar examen...', 'info');
    setTimeout(() => {
        window.open('https://t.me/Medconn_bot', '_blank');
    }, 1000);
}

function addFamilyMember() {
    showNotification('👨‍👩‍👧‍👦 Redirigiendo al ChatBot para agregar familiar...', 'info');
    setTimeout(() => {
        window.open('https://t.me/Medconn_bot', '_blank');
    }, 1000);
}

// Función para obtener el ID del usuario actual
function getCurrentUserId() {
    // Obtener del contexto global de la página
    if (window.currentUserId) {
        return window.currentUserId;
    }

    if (window.medConnectUser && window.medConnectUser.id) {
        return window.medConnectUser.id;
    }
    return null;
}

// Función para cargar consultas del usuario
async function loadConsultations() {
    const userId = getCurrentUserId();
    if (!userId) {
        console.error('No se pudo obtener el ID del usuario');
        showConsultationsError();
        return;
    }

    try {
        const response = await fetch(`/api/patient/${userId}/consultations`);
        const data = await response.json();

        document.getElementById('consultations-loading').style.display = 'none';

        if (data.consultations && data.consultations.length > 0) {
            displayConsultations(data.consultations);
        } else {
            document.getElementById('consultations-empty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error cargando consultas:', error);
        showConsultationsError();
    }
}

// Función para mostrar consultas
function displayConsultations(consultations) {
    console.log('📋 displayConsultations - Datos recibidos:', consultations);

    const container = document.getElementById('consultations-container');
    container.innerHTML = '';

    consultations.forEach((consultation, index) => {
        console.log(`📋 Consulta ${index}:`, consultation, 'ID:', consultation.id);
        const consultationElement = document.createElement('div');
        consultationElement.className = 'consultation-item d-flex align-items-center';

        const iconClass = getConsultationIcon(consultation.specialty);
        const statusBadge = getStatusBadge(consultation.status);

        consultationElement.innerHTML = `
            <div class="consultation-icon me-3">
                <i class="${iconClass}"></i>
            </div>
            <div class="flex-grow-1">
                <h6 class="mb-1">${consultation.diagnosis || 'Consulta médica'}</h6>
                <p class="text-muted mb-1">${consultation.doctor || 'Médico'} - ${consultation.specialty || 'Medicina General'}</p>
                <small class="text-muted">${formatDate(consultation.date)}</small>
            </div>
            <div class="d-flex align-items-center gap-2">
                ${statusBadge}
                <button class="btn btn-sm btn-outline-danger" onclick="deleteConsultation('${consultation.id}', event)" title="Eliminar consulta">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        container.appendChild(consultationElement);
    });
}

// Función para cargar medicamentos del usuario
async function loadMedications() {
    const userId = getCurrentUserId();
    if (!userId) {
        showMedicationsError();
        return;
    }

    try {
        document.getElementById('medications-loading').style.display = 'block';

        const response = await fetch(`/api/patient/${userId}/medications`);
        const data = await response.json();

        document.getElementById('medications-loading').style.display = 'none';

        if (data.medications && data.medications.length > 0) {
            displayMedications(data.medications);
        } else {
            document.getElementById('medications-empty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error cargando medicamentos:', error);
        showMedicationsError();
    }
}

// Función para mostrar medicamentos
function displayMedications(medications) {
    console.log('💊 displayMedications - Datos recibidos:', medications);

    const container = document.getElementById('medications-container');
    container.innerHTML = '';

    medications.forEach((medication, index) => {
        console.log(`💊 Medicamento ${index}:`, medication, 'ID:', medication.id);
        const medicationElement = document.createElement('div');
        medicationElement.className = 'medication-item d-flex align-items-center';

        const statusBadge = getMedicationStatusBadge(medication.status);

        medicationElement.innerHTML = `
            <div class="medication-icon me-3">
                <i class="fas fa-pills text-primary"></i>
            </div>
            <div class="flex-grow-1">
                <h6 class="mb-1">${medication.name || medication.medication || 'Medicamento'} ${medication.dosage || ''}</h6>
                <p class="text-muted mb-1">${medication.frequency || 'Frecuencia no especificada'}</p>
                <small class="text-muted">Prescrito por ${medication.prescribing_doctor || medication.prescribed_by || 'Médico no especificado'}</small>
            </div>
            <div class="d-flex align-items-center gap-2">
                ${statusBadge}
                <button class="btn btn-sm btn-outline-danger" onclick="deleteMedication('${medication.id}', event)" title="Eliminar medicamento">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        container.appendChild(medicationElement);
    });
}

// Función para cargar exámenes del usuario
async function loadExams() {
    const userId = getCurrentUserId();
    if (!userId) {
        showExamsError();
        return;
    }

    try {
        document.getElementById('exams-loading').style.display = 'block';

        const response = await fetch(`/api/patient/${userId}/exams`);
        const data = await response.json();

        document.getElementById('exams-loading').style.display = 'none';

        if (data.exams && data.exams.length > 0) {
            displayExams(data.exams);
        } else {
            document.getElementById('exams-empty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error cargando exámenes:', error);
        showExamsError();
    }
}

// Función para mostrar exámenes
function displayExams(exams) {
    console.log('🩺 displayExams - Datos recibidos:', exams);

    const container = document.getElementById('exams-container');
    container.innerHTML = '';

    exams.forEach((exam, index) => {
        console.log(`🩺 Examen ${index}:`, exam, 'ID:', exam.id);
        const examElement = document.createElement('div');
        examElement.className = 'exam-item d-flex align-items-center';

        const iconClass = getExamIcon(exam.exam_type);

        // Contar archivos adjuntos
        const fileCount = exam.file_url ? exam.file_url.split(',').filter(url => url.trim()).length : 0;
        const fileIndicator = fileCount > 0 ? `
            <span class="badge bg-info ms-2" title="${fileCount} archivo${fileCount > 1 ? 's' : ''} adjunto${fileCount > 1 ? 's' : ''}">
                <i class="fas fa-paperclip me-1"></i>${fileCount}
            </span>
        ` : '';

        examElement.innerHTML = `
            <div class="exam-icon me-3">
                <i class="${iconClass}"></i>
            </div>
            <div class="flex-grow-1">
                <h6 class="mb-1">
                    ${exam.exam_type}
                    ${fileIndicator}
                </h6>
                <p class="text-muted mb-1">${exam.results || 'Resultados pendientes'}</p>
                <small class="text-muted">${formatDate(exam.date)}</small>
            </div>
            <div class="d-flex align-items-center gap-2">
                <button class="btn btn-sm btn-outline-primary" onclick="viewExamDetails('${exam.exam_type}', '${exam.id}')">Ver</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteExam('${exam.id}', event)" title="Eliminar examen">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        container.appendChild(examElement);
    });
}

// Funciones auxiliares para iconos y badges
function getConsultationIcon(specialty) {
    const icons = {
        'Cardiología': 'fas fa-heartbeat text-danger',
        'Traumatología': 'fas fa-bone text-warning',
        'Medicina General': 'fas fa-user-md text-primary',
        'Neurología': 'fas fa-brain text-info',
        'Dermatología': 'fas fa-hand-holding-medical text-success'
    };
    return icons[specialty] || 'fas fa-stethoscope text-primary';
}

function getExamIcon(examType) {
    const icons = {
        'Hemograma': 'fas fa-vial text-success',
        'Electrocardiograma': 'fas fa-heartbeat text-danger',
        'Radiografía': 'fas fa-x-ray text-warning',
        'Ecografía': 'fas fa-wave-square text-info'
    };
    return icons[examType] || 'fas fa-vial text-primary';
}

function getStatusBadge(status) {
    const badges = {
        'Completada': '<span class="badge bg-success">Completada</span>',
        'Pendiente': '<span class="badge bg-warning">Pendiente</span>',
        'Cancelada': '<span class="badge bg-danger">Cancelada</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Sin estado</span>';
}

function getMedicationStatusBadge(status) {
    const badges = {
        'Activo': '<span class="badge bg-success">Activo</span>',
        'Suspendido': '<span class="badge bg-warning">Suspendido</span>',
        'Finalizado': '<span class="badge bg-secondary">Finalizado</span>'
    };
    return badges[status] || '<span class="badge bg-success">Activo</span>';
}

function formatDate(dateString) {
    if (!dateString || dateString.trim() === '' || dateString === 'null' || dateString === 'undefined') {
        return 'Fecha no especificada';
    }

    try {
        // Si ya está en formato legible español, devolverlo tal como está
        if (dateString.includes('ene') || dateString.includes('feb') || dateString.includes('mar') ||
            dateString.includes('abr') || dateString.includes('may') || dateString.includes('jun') ||
            dateString.includes('jul') || dateString.includes('ago') || dateString.includes('sep') ||
            dateString.includes('oct') || dateString.includes('nov') || dateString.includes('dic')) {
            return dateString;
        }

        // Manejar formato YYYY-MM-DD (evitar problemas de zona horaria)
        if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const parts = dateString.split('-');
            const year = parseInt(parts[0]);
            const month = parseInt(parts[1]) - 1; // JavaScript months are 0-indexed
            const day = parseInt(parts[2]);

            // Crear fecha específicamente en zona horaria local
            const date = new Date(year, month, day);

            return date.toLocaleDateString('es-CL', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
            });
        }

        // Manejar formato DD/MM/YYYY
        if (dateString.includes('/')) {
            const parts = dateString.split('/');
            if (parts.length === 3) {
                // Asumir formato DD/MM/YYYY
                const day = parseInt(parts[0]);
                const month = parseInt(parts[1]) - 1; // JavaScript months are 0-indexed
                const year = parseInt(parts[2]);

                if (day >= 1 && day <= 31 && month >= 0 && month <= 11 && year >= 1900) {
                    const parsedDate = new Date(year, month, day);
                    return parsedDate.toLocaleDateString('es-CL', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                    });
                }
            }
        }

        // Fallback: intentar crear objeto Date (puede tener problemas de zona horaria)
        const date = new Date(dateString);
        if (!isNaN(date.getTime())) {
            return date.toLocaleDateString('es-CL', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
            });
        }

        // Si no se puede parsear, devolver el string original
        return dateString;
    } catch (error) {
        console.warn('Error formateando fecha:', dateString, error);
        return dateString || 'Fecha no especificada';
    }
}

// Función para cargar familiares del usuario
async function loadFamilyMembers() {
    const userId = getCurrentUserId();
    if (!userId) {
        showFamilyError();
        return;
    }

    try {
        document.getElementById('family-loading').style.display = 'block';

        const response = await fetch(`/api/patient/${userId}/family`);
        const data = await response.json();

        document.getElementById('family-loading').style.display = 'none';

        if (data.family && data.family.length > 0) {
            displayFamilyMembers(data.family);
        } else {
            document.getElementById('family-empty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error cargando familiares:', error);
        showFamilyError();
    }
}

// Función para mostrar familiares
function displayFamilyMembers(familyMembers) {
    const container = document.getElementById('family-container');
    container.innerHTML = '';

    familyMembers.forEach(member => {
        const memberElement = document.createElement('div');
        memberElement.className = 'family-member d-flex align-items-center';

        const relationshipBadge = getRelationshipBadge(member.relationship);

        memberElement.innerHTML = `
            <div class="family-icon me-3">
                <i class="fas fa-user-friends text-info"></i>
            </div>
            <div class="flex-grow-1">
                <h6 class="mb-1">${member.name}</h6>
                <p class="text-muted mb-1">${member.phone || 'Teléfono no especificado'}</p>
                <small class="text-muted">${member.email || 'Email no especificado'}</small>
            </div>
            <div class="d-flex align-items-center gap-2">
                ${relationshipBadge}
                <button class="btn btn-sm btn-outline-danger" onclick="deleteFamilyMember('${member.id}', event)" title="Eliminar contacto">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        container.appendChild(memberElement);
    });
}

function getRelationshipBadge(relationship) {
    const badges = {
        'Madre': '<span class="badge bg-primary">Madre</span>',
        'Padre': '<span class="badge bg-primary">Padre</span>',
        'Hermana': '<span class="badge bg-info">Hermana</span>',
        'Hermano': '<span class="badge bg-info">Hermano</span>',
        'Pareja': '<span class="badge bg-success">Pareja</span>',
        'Esposa': '<span class="badge bg-success">Esposa</span>',
        'Esposo': '<span class="badge bg-success">Esposo</span>',
        'Hija': '<span class="badge bg-warning">Hija</span>',
        'Hijo': '<span class="badge bg-warning">Hijo</span>'
    };
    return badges[relationship] || `<span class="badge bg-secondary">${relationship}</span>`;
}

function showFamilyError() {
    document.getElementById('family-loading').style.display = 'none';
    document.getElementById('family-container').innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
            <h6 class="text-muted">Error cargando contactos familiares</h6>
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadFamilyMembers()">
                <i class="fas fa-refresh me-1"></i>Reintentar
            </button>
        </div>
    `;
}

// Función para cargar datos cuando se cambia de tab  
function loadTabData(tabName) {
    switch (tabName) {
        case 'medications':
            loadMedications();
            break;
        case 'exams':
            loadExams();
            break;
        case 'family':
            loadFamilyMembers();
            break;
        // history se carga automáticamente al inicio
    }
}

function viewReports() {
    showNotification('📊 Cargando reportes médicos...', 'info');
    setTimeout(() => {
        const historyTab = document.getElementById('history-tab');
        if (historyTab) {
            historyTab.click();
        }
        showNotification('✅ Reportes cargados', 'success');
    }, 1500);
}

function callEmergency() {
    if (confirm('¿Está segura de que desea contactar servicios de emergencia?')) {
        showNotification('🚨 Contactando servicios de emergencia...', 'error');
        setTimeout(() => {
            alert('Conectando con contacto de emergencia...');
        }, 1500);
    }
}

function viewExamDetails(examName, examId) {
    console.log('🔍 viewExamDetails llamada:', examName, examId);

    // Buscar los datos del examen
    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    fetch(`/api/patient/${userId}/exams`)
        .then(response => response.json())
        .then(data => {
            if (data.exams) {
                const exam = data.exams.find(e => e.id === examId || e.exam_type === examName);
                if (exam) {
                    showExamModal(exam);
                } else {
                    showNotification('Examen no encontrado', 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error cargando examen:', error);
            showNotification('Error cargando detalles del examen', 'error');
        });
}

// Navegación por tabs mejorada con carga dinámica
document.addEventListener('DOMContentLoaded', function () {
    // Cargar datos iniciales
    loadConsultations();

    // Manejar cambios de tab
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
    tabLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const tabId = this.getAttribute('data-bs-target').replace('#', '');
            loadTabData(tabId);

            // Smooth transition
            const tabContent = document.querySelector(this.getAttribute('data-bs-target'));
            if (tabContent) {
                tabContent.style.opacity = '0.7';
                setTimeout(() => {
                    tabContent.style.opacity = '1';
                }, 150);
            }
        });
    });

    // Mejorar hover effects
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList') {
                const items = document.querySelectorAll('.consultation-item, .medication-item, .exam-item, .family-member');
                items.forEach(item => {
                    if (!item.hasEventListener) {
                        item.addEventListener('mouseenter', function () {
                            this.style.transform = 'translateX(2px)';
                        });
                        item.addEventListener('mouseleave', function () {
                            this.style.transform = 'translateX(0)';
                        });
                        item.hasEventListener = true;
                    }
                });
            }
        });
    });

    // Observar cambios en contenedores
    ['consultations-container', 'medications-container', 'exams-container'].forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            observer.observe(container, { childList: true });
        }
    });
});

// Funciones para eliminar datos
async function deleteConsultation(consultationId, event) {
    console.log('🔍 deleteConsultation llamada con ID:', consultationId, 'Tipo:', typeof consultationId);

    if (!consultationId || consultationId === 'undefined' || consultationId === '') {
        showNotification('Error: ID de consulta inválido', 'error');
        console.error('❌ ID de consulta inválido:', consultationId);
        return;
    }

    const confirmed = await showCustomConfirm('Eliminar Consulta', '¿Estás seguro de que deseas eliminar esta consulta médica?', 'Esta acción no se puede deshacer y se perderá toda la información asociada.');
    if (!confirmed) {
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    // Encontrar el elemento y agregar animación de eliminación
    let consultationElement = null;
    if (event && event.target) {
        consultationElement = event.target.closest('.consultation-item');
    }
    if (consultationElement) {
        consultationElement.classList.add('deleting');
    }

    try {
        const response = await fetch(`/api/patient/${userId}/consultations/${consultationId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('✅ Consulta eliminada exitosamente', 'success');
            // Esperar un poco para que se vea la animación antes de recargar
            setTimeout(() => {
                loadConsultations();
                loadDashboardStats(); // Actualizar estadísticas
            }, 300);
        } else {
            // Remover la animación si hay error
            if (consultationElement) {
                consultationElement.classList.remove('deleting');
            }
            showNotification(data.error || 'Error eliminando la consulta', 'error');
        }
    } catch (error) {
        // Remover la animación si hay error
        if (consultationElement) {
            consultationElement.classList.remove('deleting');
        }
        console.error('Error eliminando consulta:', error);
        showNotification('Error de conexión al eliminar la consulta', 'error');
    }
}

async function deleteMedication(medicationId, event) {
    console.log('🔍 deleteMedication llamada con ID:', medicationId, 'Tipo:', typeof medicationId);

    if (!medicationId || medicationId === 'undefined' || medicationId === '') {
        showNotification('Error: ID de medicamento inválido', 'error');
        console.error('❌ ID de medicamento inválido:', medicationId);
        return;
    }

    const confirmed = await showCustomConfirm('Eliminar Medicamento', '¿Estás seguro de que deseas eliminar este medicamento?', 'Esta acción no se puede deshacer y se perderá el historial de prescripción.');
    if (!confirmed) {
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    // Encontrar el elemento y agregar animación de eliminación
    let medicationElement = null;
    if (event && event.target) {
        medicationElement = event.target.closest('.medication-item');
    }
    if (medicationElement) {
        medicationElement.classList.add('deleting');
    }

    try {
        const response = await fetch(`/api/patient/${userId}/medications/${medicationId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('✅ Medicamento eliminado exitosamente', 'success');
            setTimeout(() => {
                loadMedications();
                loadDashboardStats(); // Actualizar estadísticas
            }, 300);
        } else {
            if (medicationElement) {
                medicationElement.classList.remove('deleting');
            }
            showNotification(data.error || 'Error eliminando el medicamento', 'error');
        }
    } catch (error) {
        if (medicationElement) {
            medicationElement.classList.remove('deleting');
        }
        console.error('Error eliminando medicamento:', error);
        showNotification('Error de conexión al eliminar el medicamento', 'error');
    }
}

async function deleteExam(examId, event) {
    console.log('🔍 deleteExam llamada con ID:', examId, 'Tipo:', typeof examId);

    if (!examId || examId === 'undefined' || examId === '') {
        showNotification('Error: ID de examen inválido', 'error');
        console.error('❌ ID de examen inválido:', examId);
        return;
    }

    const confirmed = await showCustomConfirm('Eliminar Examen', '¿Estás seguro de que deseas eliminar este examen médico?', 'Esta acción no se puede deshacer y se perderán los resultados asociados.');
    if (!confirmed) {
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    // Encontrar el elemento y agregar animación de eliminación
    let examElement = null;
    if (event && event.target) {
        examElement = event.target.closest('.exam-item');
    }
    if (examElement) {
        examElement.classList.add('deleting');
    }

    try {
        const response = await fetch(`/api/patient/${userId}/exams/${examId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('✅ Examen eliminado exitosamente', 'success');
            setTimeout(() => {
                loadExams();
                loadDashboardStats(); // Actualizar estadísticas
            }, 300);
        } else {
            if (examElement) {
                examElement.classList.remove('deleting');
            }
            showNotification(data.error || 'Error eliminando el examen', 'error');
        }
    } catch (error) {
        if (examElement) {
            examElement.classList.remove('deleting');
        }
        console.error('Error eliminando examen:', error);
        showNotification('Error de conexión al eliminar el examen', 'error');
    }
}

async function deleteFamilyMember(familyId, event) {
    const confirmed = await showCustomConfirm('Eliminar Contacto Familiar', '¿Estás seguro de que deseas eliminar este contacto familiar?', 'Esta acción no se puede deshacer y se perderá la información de contacto.');
    if (!confirmed) {
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    // Encontrar el elemento y agregar animación de eliminación
    let familyElement = null;
    if (event && event.target) {
        familyElement = event.target.closest('.family-member');
    }
    if (familyElement) {
        familyElement.classList.add('deleting');
    }

    try {
        const response = await fetch(`/api/patient/${userId}/family/${familyId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('✅ Contacto familiar eliminado exitosamente', 'success');
            setTimeout(() => {
                loadFamilyMembers();
            }, 300);
        } else {
            if (familyElement) {
                familyElement.classList.remove('deleting');
            }
            showNotification(data.error || 'Error eliminando el contacto familiar', 'error');
        }
    } catch (error) {
        if (familyElement) {
            familyElement.classList.remove('deleting');
        }
        console.error('Error eliminando contacto familiar:', error);
        showNotification('Error de conexión al eliminar el contacto familiar', 'error');
    }
}

// Funciones de error
function showConsultationsError() {
    document.getElementById('consultations-loading').style.display = 'none';
    document.getElementById('consultations-container').innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
            <h6 class="text-muted">Error cargando consultas</h6>
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadConsultations()">
                <i class="fas fa-refresh me-1"></i>Reintentar
            </button>  
        </div>
    `;
}

function showMedicationsError() {
    document.getElementById('medications-loading').style.display = 'none';
    document.getElementById('medications-container').innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
            <h6 class="text-muted">Error cargando medicamentos</h6>
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadMedications()">
                <i class="fas fa-refresh me-1"></i>Reintentar
            </button>
        </div>
    `;
}

function showExamsError() {
    document.getElementById('exams-loading').style.display = 'none';
    document.getElementById('exams-container').innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
            <h6 class="text-muted">Error cargando exámenes</h6>
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadExams()">
                <i class="fas fa-refresh me-1"></i>Reintentar
            </button>
        </div>
    `;
}

// Sistema de notificaciones (reutilizado)
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    notification.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <div class="flex-grow-1">
                <div class="fw-medium">${message}</div>
            </div>
            <button class="btn-close btn-sm ms-2" onclick="this.closest('.notification').remove()"></button>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// === FUNCIONES DE TELEGRAM ===

// Función para verificar el estado de vinculación con Telegram
async function checkTelegramStatus() {
    try {
        const response = await fetch('/api/user/telegram-status');
        const data = await response.json();

        document.getElementById('telegram-status').style.display = 'none';

        if (data.is_linked) {
            // Mostrar interfaz de cuenta vinculada
            document.getElementById('telegram-linked').style.display = 'block';
            document.getElementById('telegram-not-linked').style.display = 'none';
            document.getElementById('linked-telegram-id').textContent = data.telegram_id;
            document.getElementById('bot-exams-count').textContent = data.exams_from_bot || 0;
        } else {
            // Mostrar interfaz para vincular
            document.getElementById('telegram-not-linked').style.display = 'block';
            document.getElementById('telegram-linked').style.display = 'none';
        }
    } catch (error) {
        console.error('Error verificando estado de Telegram:', error);
        document.getElementById('telegram-status').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error al verificar el estado de vinculación con Telegram
            </div>
        `;
    }
}

// Función para vincular cuenta de Telegram
function linkTelegramAccount() {
    const telegramId = document.getElementById('telegram-id-input').value.trim();

    if (!telegramId) {
        showNotification('Por favor ingresa tu ID de Telegram', 'error');
        return;
    }

    // Validar que sea un número
    if (!/^\d+$/.test(telegramId)) {
        showNotification('El ID de Telegram debe ser solo números', 'error');
        return;
    }

    fetch('/api/user/link-telegram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            telegram_id: telegramId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mensaje de éxito con información detallada
                let successMessage = `¡Cuenta vinculada exitosamente!<br>
                                 <strong>Usuario:</strong> ${data.user_name || 'N/A'}<br>
                                 <strong>Telegram ID:</strong> ${data.telegram_id}`;

                if (data.exams_found > 0) {
                    successMessage += `<br><strong>📊 Exámenes encontrados:</strong> ${data.exams_found}`;
                }

                if (data.welcome_message_sent) {
                    successMessage += `<br><br>💬 <strong>¡Revisa tu Telegram!</strong><br>Te hemos enviado un mensaje de bienvenida.`;
                } else {
                    successMessage += `<br><br>⚠️ No pudimos enviar el mensaje automático a Telegram, pero la vinculación fue exitosa.`;
                }

                showNotification(successMessage, 'success');

                // Limpiar el input
                document.getElementById('telegram-id-input').value = '';

                // Refrescar el estado
                setTimeout(() => {
                    checkTelegramStatus();
                    loadExams(); // Recargar exámenes por si hay nuevos
                }, 2000);
            } else {
                showNotification(data.error || 'Error vinculando cuenta', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión. Intenta de nuevo.', 'error');
        });
}

// Función para desvincular cuenta de Telegram
async function unlinkTelegramAccount() {
    if (!confirm('¿Estás seguro de que deseas desvincular tu cuenta de Telegram? Los datos ya registrados se mantendrán.')) {
        return;
    }

    try {
        const response = await fetch('/api/user/link-telegram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: ''  // Enviar vacío para desvincular
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('Cuenta de Telegram desvinculada exitosamente', 'success');
            checkTelegramStatus();
        } else {
            showNotification(data.error || 'Error desvinculando cuenta', 'error');
        }
    } catch (error) {
        console.error('Error desvinculando Telegram:', error);
        showNotification('Error de conexión al desvincular Telegram', 'error');
    }
}

// Función para cargar estadísticas del dashboard
async function loadDashboardStats() {
    const userId = getCurrentUserId();
    if (!userId) {
        console.error('No se pudo obtener el ID del usuario');
        return;
    }

    try {
        const response = await fetch(`/api/patient/${userId}/stats`);
        const data = await response.json();

        if (response.ok) {
            // Actualizar estadísticas en el dashboard
            const consultationsCount = document.getElementById('consultations-count');
            const medicationsCount = document.getElementById('medications-count');
            const healthScore = document.getElementById('health-score');

            if (consultationsCount) {
                consultationsCount.innerHTML = data.consultations || 0;
            }

            if (medicationsCount) {
                medicationsCount.innerHTML = data.medications || 0;
            }

            if (healthScore) {
                healthScore.innerHTML = `${data.health_score || 95}%`;
            }

            console.log('📊 Estadísticas cargadas:', data);
        } else {
            console.error('Error cargando estadísticas:', data.error);
            // Mostrar valores por defecto en caso de error
            const consultationsCount = document.getElementById('consultations-count');
            const medicationsCount = document.getElementById('medications-count');
            const healthScore = document.getElementById('health-score');

            if (consultationsCount) consultationsCount.innerHTML = '0';
            if (medicationsCount) medicationsCount.innerHTML = '0';
            if (healthScore) healthScore.innerHTML = '95%';
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        // Mostrar valores por defecto en caso de error
        const consultationsCount = document.getElementById('consultations-count');
        const medicationsCount = document.getElementById('medications-count');
        const healthScore = document.getElementById('health-score');

        if (consultationsCount) consultationsCount.innerHTML = '0';
        if (medicationsCount) medicationsCount.innerHTML = '0';
        if (healthScore) healthScore.innerHTML = '95%';
    }
}

// Cargar estadísticas cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    // Cargar estadísticas del dashboard
    loadDashboardStats();

    // Cargar datos iniciales de las pestañas
    loadConsultations();

    // Verificar estado de Telegram
    checkTelegramStatus();
});

// Agregar event listener para verificar Telegram cuando se muestre la pestaña
document.addEventListener('DOMContentLoaded', function () {
    // Verificar cuando se hace clic en la pestaña de Telegram
    const telegramTab = document.getElementById('telegram-tab');
    if (telegramTab) {
        telegramTab.addEventListener('shown.bs.tab', function () {
            checkTelegramStatus();
        });
    }

    // Si ya estamos en la pestaña de Telegram al cargar la página
    if (window.location.hash === '#telegram') {
        setTimeout(checkTelegramStatus, 500);
    }
});

// === FIN FUNCIONES DE TELEGRAM ===

// === MODAL DE DETALLES DE EXAMEN ===

function showExamModal(exam) {
    console.log('📋 Mostrando modal para examen:', exam);

    // Crear el modal
    const modal = document.createElement('div');
    modal.className = 'exam-modal';
    modal.innerHTML = `
        <div class="exam-modal-overlay">
            <div class="exam-modal-dialog">
                <div class="exam-modal-header">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file-medical text-primary me-2"></i>
                        <h4 class="mb-0">${exam.exam_type}</h4>
                    </div>
                    <button class="btn-close" onclick="window.closeExamModal()"></button>
                </div>
                
                <div class="exam-modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="exam-info">
                                <h6><i class="fas fa-calendar me-2"></i>Información del Examen</h6>
                                <div class="info-item">
                                    <strong>Fecha:</strong> ${formatDate(exam.date)}
                                </div>
                                <div class="info-item">
                                    <strong>Laboratorio:</strong> ${exam.lab || 'No especificado'}
                                </div>
                                <div class="info-item">
                                    <strong>Médico:</strong> ${exam.doctor || 'No especificado'}
                                </div>
                                <div class="info-item">
                                    <strong>Estado:</strong> ${exam.status || 'Completado'}
                                </div>
                            </div>
                            
                            <div class="exam-results mt-3">
                                <h6><i class="fas fa-clipboard-list me-2"></i>Resultados</h6>
                                <div class="results-content">
                                    ${exam.results || 'Resultados no disponibles'}
                                </div>
                            </div>
                            
                            <div class="exam-documents mt-3">
                                <h6><i class="fas fa-folder-open me-2"></i>Documentos</h6>
                                <div class="documents-content" id="exam-documents-summary">
                                    ${getDocumentsSummary(exam.file_url)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="exam-files">
                                <h6><i class="fas fa-paperclip me-2"></i>Archivos Adjuntos</h6>
                                
                                <div id="exam-file-display">
                                    ${getMultipleFilesDisplay(exam.file_url)}
                                </div>
                                
                                <div class="upload-section mt-3">
                                    <h6><i class="fas fa-upload me-2"></i>Subir Archivos</h6>
                                    <form id="upload-form" enctype="multipart/form-data">
                                        <div class="mb-2">
                                            <input type="file" class="form-control" id="exam-files" 
                                                   accept=".pdf,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.dcm,.dicom,.doc,.docx,.txt"
                                                   multiple>
                                            <div class="form-text">
                                                <i class="fas fa-info-circle me-1"></i>
                                                <strong>Múltiples archivos:</strong> Mantén presionado Ctrl (Windows) o Cmd (Mac) para seleccionar varios archivos.
                                                <br>Formatos permitidos: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM, DOC, DOCX, TXT (máx. 16MB cada uno)
                                            </div>
                                        </div>
                                        <div id="selected-files-preview" class="mb-2" style="display: none;">
                                            <small class="text-muted">Archivos seleccionados:</small>
                                            <div id="files-list" class="mt-1"></div>
                                        </div>
                                        <div class="d-flex gap-2">
                                            <button type="button" class="btn btn-success btn-sm" onclick="uploadMultipleExamFiles('${exam.id}')">
                                                <i class="fas fa-upload me-1"></i>Subir Archivos
                                            </button>
                                            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="clearFileSelection()">
                                                <i class="fas fa-times me-1"></i>Limpiar
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="exam-modal-footer">
                    <button class="btn btn-secondary" onclick="window.closeExamModal()">Cerrar</button>
                    <button class="btn btn-primary" onclick="printExam('${exam.id}')">
                        <i class="fas fa-print me-1"></i>Imprimir
                    </button>
                </div>
            </div>
        </div>
    `;

    // Agregar estilos
    const style = document.createElement('style');
    style.textContent = `
        .exam-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .exam-modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease-out;
        }
        
        .exam-modal-dialog {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 95%;
            max-height: 90vh;
            overflow: hidden;
            animation: slideIn 0.3s ease-out;
        }
        
        .exam-modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8f9fa;
        }
        
        .exam-modal-body {
            padding: 24px;
            max-height: 60vh;
            overflow-y: auto;
        }
        
        .exam-modal-footer {
            padding: 16px 24px;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            background: #f8f9fa;
        }
        
        .exam-info, .exam-results, .exam-documents, .exam-files {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        .info-item {
            margin-bottom: 8px;
            padding: 4px 0;
        }
        
        .results-content {
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            min-height: 60px;
        }
        
        .file-preview {
            background: white;
            padding: 16px;
            border-radius: 8px;
            border: 2px dashed #dee2e6;
            text-align: center;
        }
        
        .file-preview img {
            max-width: 100%;
            max-height: 200px;
            border-radius: 4px;
        }
        
        .upload-section {
            background: #e3f2fd;
            padding: 16px;
            border-radius: 8px;
        }
        
        .documents-content {
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #28a745;
            min-height: 60px;
        }
        
        .documents-summary {
            display: flex;
            flex-direction: column;
        }
        
        .documents-summary-empty {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .documents-breakdown {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }
        
        .doc-type-badge {
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
            border: 1px solid #dee2e6;
        }
        
        .documents-action {
            border-top: 1px solid #e9ecef;
            padding-top: 8px;
            margin-top: 8px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { 
                opacity: 0;
                transform: translateY(-20px) scale(0.95);
            }
            to { 
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
    `;

    // Función para limpiar el modal
    const closeModalFunction = () => {
        if (document.body.contains(modal)) {
            document.body.removeChild(modal);
        }
        if (document.head.contains(style)) {
            document.head.removeChild(style);
        }
        document.removeEventListener('keydown', handleEscape);
        if (window.closeExamModal) {
            delete window.closeExamModal;
        }
    };

    // Asignar la función globalmente
    window.closeExamModal = closeModalFunction;

    // Manejar escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            closeModalFunction();
        }
    };

    // Agregar al DOM
    document.head.appendChild(style);
    document.body.appendChild(modal);
    document.addEventListener('keydown', handleEscape);

    // Cerrar al hacer clic en el overlay
    modal.querySelector('.exam-modal-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeModalFunction();
        }
    });

    // Event listener para mostrar vista previa de archivos seleccionados
    const fileInput = modal.querySelector('#exam-files');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            showSelectedFilesPreview(this.files);
        });
    }
}

function getFilePreview(fileUrl) {
    if (!fileUrl) return '<p class="text-muted">No hay archivo</p>';

    const extension = fileUrl.split('.').pop().toLowerCase();
    const fileName = fileUrl.split('/').pop();

    if (['png', 'jpg', 'jpeg', 'gif', 'bmp'].includes(extension)) {
        return `
            <div class="image-preview">
                <img src="${fileUrl}" alt="Vista previa" class="img-fluid">
                <p class="mt-2 text-muted">${fileName}</p>
            </div>
        `;
    } else if (extension === 'pdf') {
        return `
            <div class="pdf-preview">
                <i class="fas fa-file-pdf fa-3x text-danger"></i>
                <p class="mt-2">${fileName}</p>
                <small class="text-muted">Archivo PDF</small>
            </div>
        `;
    } else {
        return `
            <div class="file-preview">
                <i class="fas fa-file fa-3x text-secondary"></i>
                <p class="mt-2">${fileName}</p>
                <small class="text-muted">Archivo médico</small>
            </div>
        `;
    }
}

function getDocumentsSummary(fileUrls) {
    console.log('📋 Generando resumen de documentos:', fileUrls);

    if (!fileUrls || fileUrls.trim() === '') {
        console.log('📝 Sin URLs de archivos - retornando estado vacío');
        return `
            <div class="documents-summary-empty">
                <i class="fas fa-inbox text-muted me-2"></i>
                <span class="text-muted">Sin documentos asociados</span>
            </div>
        `;
    }

    // Dividir por comas y limpiar espacios
    const urls = fileUrls.split(',').map(url => url.trim()).filter(url => url);
    console.log('📁 URLs procesadas:', urls);
    console.log('📊 Número de archivos:', urls.length);

    if (urls.length === 0) {
        console.log('📝 Sin URLs válidas - retornando estado vacío');
        return `
            <div class="documents-summary-empty">
                <i class="fas fa-inbox text-muted me-2"></i>
                <span class="text-muted">Sin documentos asociados</span>
            </div>
        `;
    }

    // Contar tipos de archivos
    const fileTypes = {
        'pdf': 0,
        'images': 0,
        'text': 0,
        'medical': 0,
        'word': 0,
        'other': 0
    };

    urls.forEach(url => {
        const fileName = url.split('/').pop();
        const fileExt = fileName.split('.').pop().toLowerCase();

        if (fileExt === 'pdf') {
            fileTypes.pdf++;
        } else if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(fileExt)) {
            fileTypes.images++;
        } else if (['txt'].includes(fileExt)) {
            fileTypes.text++;
        } else if (['dcm', 'dicom'].includes(fileExt)) {
            fileTypes.medical++;
        } else if (['doc', 'docx'].includes(fileExt)) {
            fileTypes.word++;
        } else {
            fileTypes.other++;
        }
    });

    let summaryHtml = `
        <div class="documents-summary">
            <div class="documents-count mb-2">
                <span class="badge bg-primary">
                    <i class="fas fa-paperclip me-1"></i>
                    ${urls.length} documento${urls.length > 1 ? 's' : ''} total${urls.length > 1 ? 'es' : ''}
                </span>
            </div>
            <div class="documents-breakdown">
    `;

    // Mostrar breakdown por tipos
    if (fileTypes.pdf > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file-pdf text-danger me-1"></i>
                ${fileTypes.pdf} PDF${fileTypes.pdf > 1 ? 's' : ''}
            </span>
        `;
    }

    if (fileTypes.images > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file-image text-info me-1"></i>
                ${fileTypes.images} Imagen${fileTypes.images > 1 ? 'es' : ''}
            </span>
        `;
    }

    if (fileTypes.medical > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file-medical text-primary me-1"></i>
                ${fileTypes.medical} DICOM${fileTypes.medical > 1 ? 's' : ''}
            </span>
        `;
    }

    if (fileTypes.word > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file-word text-primary me-1"></i>
                ${fileTypes.word} Word${fileTypes.word > 1 ? 's' : ''}
            </span>
        `;
    }

    if (fileTypes.text > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file-alt text-secondary me-1"></i>
                ${fileTypes.text} Texto${fileTypes.text > 1 ? 's' : ''}
            </span>
        `;
    }

    if (fileTypes.other > 0) {
        summaryHtml += `
            <span class="doc-type-badge me-1 mb-1">
                <i class="fas fa-file text-secondary me-1"></i>
                ${fileTypes.other} Otro${fileTypes.other > 1 ? 's' : ''}
            </span>
        `;
    }

    summaryHtml += `
            </div>
            <div class="documents-action mt-2">
                <small class="text-muted">
                    <i class="fas fa-arrow-right me-1"></i>
                    Ver todos en "Archivos Adjuntos"
                </small>
            </div>
        </div>
    `;

    console.log('📋 Resumen de documentos generado:', {
        totalFiles: urls.length,
        fileTypes: fileTypes,
        htmlLength: summaryHtml.length
    });

    return summaryHtml;
}

function getMultipleFilesDisplay(fileUrls) {
    console.log('📎 Procesando archivos:', fileUrls);

    if (!fileUrls || fileUrls.trim() === '') {
        return '<p class="text-muted"><i class="fas fa-info-circle me-2"></i>No hay archivos adjuntos</p>';
    }

    // Dividir por comas y limpiar espacios
    const urls = fileUrls.split(',').map(url => url.trim()).filter(url => url);

    if (urls.length === 0) {
        return '<p class="text-muted"><i class="fas fa-info-circle me-2"></i>No hay archivos adjuntos</p>';
    }

    console.log('📁 Archivos encontrados:', urls.length);

    let html = `<div class="files-grid">`;

    urls.forEach((url, index) => {
        const fileName = url.split('/').pop();
        const fileExt = fileName.split('.').pop().toLowerCase();

        // Iconos por tipo de archivo
        const fileIcons = {
            'pdf': 'fas fa-file-pdf text-danger',
            'png': 'fas fa-file-image text-info',
            'jpg': 'fas fa-file-image text-info',
            'jpeg': 'fas fa-file-image text-info',
            'gif': 'fas fa-file-image text-info',
            'bmp': 'fas fa-file-image text-info',
            'tiff': 'fas fa-file-image text-info',
            'dcm': 'fas fa-file-medical text-primary',
            'dicom': 'fas fa-file-medical text-primary',
            'doc': 'fas fa-file-word text-primary',
            'docx': 'fas fa-file-word text-primary',
            'txt': 'fas fa-file-alt text-secondary'
        };

        const iconClass = fileIcons[fileExt] || 'fas fa-file text-secondary';

        html += `
            <div class="file-item clickable-file" style="margin-bottom: 12px; padding: 12px; border: 1px solid #dee2e6; border-radius: 8px; background: #f8f9fa; cursor: pointer; transition: all 0.2s ease;" 
                 onclick="previewFile('${url}', '${fileName}', '${fileExt}')" 
                 onmouseover="this.style.backgroundColor='#e3f2fd'; this.style.borderColor='#2196f3';" 
                 onmouseout="this.style.backgroundColor='#f8f9fa'; this.style.borderColor='#dee2e6';">
                <div class="d-flex align-items-center">
                    <div class="file-icon me-3">
                        <i class="${iconClass} fa-2x"></i>
                    </div>
                    <div class="file-details flex-grow-1">
                        <div class="file-name fw-bold">${fileName}</div>
                        <small class="text-muted">
                            <i class="fas fa-mouse-pointer me-1"></i>
                            Haz clic para visualizar • ${fileExt.toUpperCase()}
                        </small>
                    </div>
                    <div class="file-actions" onclick="event.stopPropagation();">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="previewFile('${url}', '${fileName}', '${fileExt}')" title="Vista previa">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success me-1" onclick="openFile('${url}')" title="Abrir en nueva pestaña">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="downloadFile('${url}')" title="Descargar archivo">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    html += `</div>`;

    if (urls.length > 1) {
        html += `
            <div class="files-summary mt-2">
                <small class="text-muted">
                    <i class="fas fa-paperclip me-1"></i>
                    ${urls.length} archivo${urls.length > 1 ? 's' : ''} adjunto${urls.length > 1 ? 's' : ''}
                </small>
            </div>
        `;
    }

    return html;
}

function openFile(fileUrl) {
    window.open(fileUrl, '_blank');
}

function downloadFile(fileUrl) {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileUrl.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function previewFile(fileUrl, fileName, fileExt) {
    console.log('👁️ Previsualizando archivo:', fileName, fileExt);

    // Crear modal de vista previa
    const modal = document.createElement('div');
    modal.className = 'file-preview-modal';
    modal.innerHTML = `
        <div class="file-preview-overlay">
            <div class="file-preview-dialog">
                <div class="file-preview-header">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file-alt text-primary me-2"></i>
                        <h5 class="mb-0">${fileName}</h5>
                    </div>
                    <button class="btn-close" onclick="closeFilePreview()"></button>
                </div>
                
                <div class="file-preview-body">
                    <div id="file-content">
                        ${getFilePreviewContent(fileUrl, fileName, fileExt)}
                    </div>
                </div>
                
                <div class="file-preview-footer">
                    <button class="btn btn-secondary me-2" onclick="closeFilePreview()">
                        <i class="fas fa-times me-1"></i>Cerrar
                    </button>
                    <button class="btn btn-primary me-2" onclick="openFile('${fileUrl}')">
                        <i class="fas fa-external-link-alt me-1"></i>Abrir en Nueva Pestaña
                    </button>
                    <button class="btn btn-success" onclick="downloadFile('${fileUrl}')">
                        <i class="fas fa-download me-1"></i>Descargar
                    </button>
                </div>
            </div>
        </div>
    `;

    // Agregar estilos del modal
    const style = document.createElement('style');
    style.textContent = `
        .file-preview-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .file-preview-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(3px);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease-out;
        }
        
        .file-preview-dialog {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            max-width: 90vw;
            max-height: 90vh;
            width: 800px;
            overflow: hidden;
            animation: zoomIn 0.3s ease-out;
        }
        
        .file-preview-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8f9fa;
        }
        
        .file-preview-body {
            padding: 24px;
            max-height: 60vh;
            overflow-y: auto;
            background: #fff;
        }
        
        .file-preview-footer {
            padding: 16px 24px;
            border-top: 1px solid #e9ecef;
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            background: #f8f9fa;
        }
        
        .file-content-container {
            text-align: center;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        
        .file-preview-image {
            max-width: 100%;
            max-height: 500px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .file-preview-text {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            text-align: left;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .file-preview-pdf {
            width: 100%;
            height: 500px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
        
        .file-preview-unsupported {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes zoomIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    `;

    // Agregar al DOM
    document.head.appendChild(style);
    document.body.appendChild(modal);

    // Manejar tecla Escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            closeFilePreview();
        }
    };
    document.addEventListener('keydown', handleEscape);

    // Función para cerrar
    window.closeFilePreview = () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.removeChild(modal);
        document.head.removeChild(style);
        delete window.closeFilePreview;
    };

    // Cerrar al hacer clic en el overlay
    modal.querySelector('.file-preview-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeFilePreview();
        }
    });
}

function getFilePreviewContent(fileUrl, fileName, fileExt) {
    const ext = fileExt.toLowerCase();

    // Imágenes
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(ext)) {
        return `
            <div class="file-content-container">
                <img src="${fileUrl}" alt="${fileName}" class="file-preview-image" 
                     onerror="this.parentElement.innerHTML='<div class=\\"file-preview-unsupported\\"><i class=\\"fas fa-exclamation-triangle fa-3x mb-3\\"></i><h5>Error al cargar la imagen</h5><p>No se pudo cargar la imagen. Puede estar corrupta o no ser accesible.</p></div>'">
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Imagen ${ext.toUpperCase()} • Haz clic y arrastra para mover
                    </small>
                </div>
            </div>
        `;
    }

    // PDFs
    if (ext === 'pdf') {
        return `
            <div class="file-content-container">
                <iframe src="${fileUrl}" class="file-preview-pdf" 
                        onerror="this.parentElement.innerHTML='<div class=\\"file-preview-unsupported\\"><i class=\\"fas fa-file-pdf fa-3x mb-3 text-danger\\"></i><h5>Vista previa no disponible</h5><p>No se puede mostrar el PDF en el navegador. Usa el botón \\"Abrir en Nueva Pestaña\\" para verlo.</p></div>'">
                </iframe>
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Documento PDF • Usa los controles del visor para navegar
                    </small>
                </div>
            </div>
        `;
    }

    // Archivos de texto
    if (['txt'].includes(ext)) {
        // Para archivos de texto, intentamos cargar el contenido
        return `
            <div class="file-content-container">
                <div class="file-preview-text" id="text-content-${Date.now()}">
                    <div class="text-center">
                        <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                        <p>Cargando contenido del archivo...</p>
                    </div>
                </div>
                <div class="mt-3">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Archivo de texto • ${fileName}
                    </small>
                </div>
            </div>
            <script>
                fetch('${fileUrl}')
                    .then(response => response.text())
                    .then(text => {
                        const container = document.getElementById('text-content-${Date.now()}');
                        if (container) {
                            container.innerHTML = text || 'El archivo está vacío.';
                        }
                    })
                    .catch(error => {
                        const container = document.getElementById('text-content-${Date.now()}');
                        if (container) {
                            container.innerHTML = '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle mb-2"></i><br>Error al cargar el contenido del archivo.</div>';
                        }
                    });
            </script>
        `;
    }

    // Archivos médicos (DICOM, DCM)
    if (['dcm', 'dicom'].includes(ext)) {
        return `
            <div class="file-content-container file-preview-unsupported">
                <i class="fas fa-file-medical fa-4x mb-3 text-primary"></i>
                <h5>Archivo Médico ${ext.toUpperCase()}</h5>
                <p>Los archivos DICOM requieren un visor especializado.</p>
                <p class="text-muted">Usa "Abrir en Nueva Pestaña" o "Descargar" para usar un visor DICOM apropiado.</p>
                <div class="mt-3">
                    <small class="badge bg-info">
                        <i class="fas fa-stethoscope me-1"></i>
                        Imagen Médica
                    </small>
                </div>
            </div>
        `;
    }

    // Documentos de Word
    if (['doc', 'docx'].includes(ext)) {
        return `
            <div class="file-content-container file-preview-unsupported">
                <i class="fas fa-file-word fa-4x mb-3 text-primary"></i>
                <h5>Documento de Word</h5>
                <p>Los documentos de Word no se pueden previsualizar directamente.</p>
                <p class="text-muted">Usa "Abrir en Nueva Pestaña" para verlo en tu navegador o "Descargar" para abrirlo en Word.</p>
                <div class="mt-3">
                    <small class="badge bg-primary">
                        <i class="fas fa-file-word me-1"></i>
                        ${fileName}
                    </small>
                </div>
            </div>
        `;
    }

    // Tipo de archivo no soportado
    return `
        <div class="file-content-container file-preview-unsupported">
            <i class="fas fa-file fa-4x mb-3 text-secondary"></i>
            <h5>Vista previa no disponible</h5>
            <p>No se puede mostrar una vista previa para este tipo de archivo (${ext.toUpperCase()}).</p>
            <p class="text-muted">Usa "Abrir en Nueva Pestaña" o "Descargar" para ver el archivo.</p>
            <div class="mt-3">
                <small class="badge bg-secondary">
                    <i class="fas fa-file me-1"></i>
                    ${fileName}
                </small>
            </div>
        </div>
    `;
}

function showSelectedFilesPreview(files) {
    const preview = document.getElementById('selected-files-preview');
    const filesList = document.getElementById('files-list');

    if (!files || files.length === 0) {
        preview.style.display = 'none';
        return;
    }

    let html = '';
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
        const fileExt = file.name.split('.').pop().toLowerCase();

        // Iconos por tipo de archivo
        const fileIcons = {
            'pdf': 'fas fa-file-pdf text-danger',
            'png': 'fas fa-file-image text-info',
            'jpg': 'fas fa-file-image text-info',
            'jpeg': 'fas fa-file-image text-info',
            'gif': 'fas fa-file-image text-info',
            'doc': 'fas fa-file-word text-primary',
            'docx': 'fas fa-file-word text-primary',
            'txt': 'fas fa-file-alt text-secondary'
        };

        const iconClass = fileIcons[fileExt] || 'fas fa-file text-secondary';

        html += `
            <div class="d-flex align-items-center mb-1 p-2 bg-light rounded">
                <i class="${iconClass} me-2"></i>
                <span class="flex-grow-1">${file.name}</span>
                <small class="text-muted">${fileSize} MB</small>
            </div>
        `;
    }

    filesList.innerHTML = html;
    preview.style.display = 'block';
}

function clearFileSelection() {
    const fileInput = document.getElementById('exam-files');
    if (fileInput) {
        fileInput.value = '';
        showSelectedFilesPreview([]);
    }
}

async function updateExamModalFiles(examId, retryCount = 0) {
    /**
     * Actualiza solo la sección de archivos del modal existente
     * sin cerrarlo ni crear uno nuevo
     */
    try {
        const userId = getCurrentUserId();
        if (!userId) return;

        console.log(`🔄 Actualizando modal (intento ${retryCount + 1})...`);

        // Obtener datos actualizados del examen
        const response = await fetch(`/api/patient/${userId}/exams`);
        if (!response.ok) {
            console.error('❌ Error en response:', response.status);
            return;
        }

        const data = await response.json();
        if (!data.success) {
            console.error('❌ Error en data:', data);
            return;
        }

        // Buscar el examen específico
        const exam = data.exams.find(e => e.id === examId);
        if (!exam) {
            console.error('❌ Examen no encontrado:', examId);
            return;
        }

        console.log('📋 Examen encontrado:', exam.exam_type);
        console.log('📎 URLs de archivos:', exam.file_url);

        // Contar archivos actuales
        const currentFileUrls = exam.file_url || '';
        const currentFileCount = currentFileUrls && currentFileUrls.trim() ?
            currentFileUrls.split(',').map(url => url.trim()).filter(url => url).length : 0;

        console.log('📊 Número de archivos encontrados:', currentFileCount);

        // Verificar si realmente hay archivos nuevos (en caso de reintentos)
        if (retryCount > 0 && currentFileCount === 0) {
            console.warn('⚠️ Aún no se detectan archivos, puede necesitar más tiempo...');
        }

        // Actualizar la sección de archivos adjuntos
        const fileDisplaySection = document.getElementById('exam-file-display');
        if (fileDisplaySection) {
            const fileUrls = exam.file_url || '';
            console.log('🔄 Actualizando sección de archivos adjuntos...');

            if (fileUrls && fileUrls.trim()) {
                fileDisplaySection.innerHTML = getMultipleFilesDisplay(fileUrls);
                console.log('✅ Archivos adjuntos actualizados');
            } else {
                fileDisplaySection.innerHTML = '<p class="text-muted mb-0">No hay archivos adjuntos</p>';
                console.log('📝 Sin archivos adjuntos');
            }
        } else {
            console.error('❌ No se encontró la sección exam-file-display');
        }

        // Actualizar la sección de resumen de documentos
        const documentsSection = document.getElementById('exam-documents-summary');
        if (documentsSection) {
            const fileUrls = exam.file_url || '';
            console.log('📁 Actualizando sección de documentos...');
            console.log('📎 URLs para documentos:', fileUrls);

            const documentsSummary = getDocumentsSummary(fileUrls);
            documentsSection.innerHTML = documentsSummary;
            console.log('✅ Sección de documentos actualizada');
        } else {
            console.error('❌ No se encontró la sección exam-documents-summary');
        }

        // Limpiar la selección de archivos
        clearFileSelection();

        // Debug: Verificar estado final de los elementos
        const displayedCount = debugModalElements();

        // Verificar que la actualización fue exitosa
        if (displayedCount > 0) {
            console.log('✅ Modal actualizado con nuevos archivos');
            verifyDocumentsUpdate();
        } else if (currentFileCount > 0) {
            console.warn('⚠️ Hay archivos pero no se muestran en la UI - posible problema de sincronización');
        }

    } catch (error) {
        console.error('Error actualizando modal:', error);

        // Reintentar hasta 3 veces con delay incremental
        if (retryCount < 3) {
            const delay = (retryCount + 1) * 500; // 500ms, 1000ms, 1500ms
            console.log(`🔄 Reintentando en ${delay}ms...`);
            setTimeout(() => {
                updateExamModalFiles(examId, retryCount + 1);
            }, delay);
        } else {
            console.error('❌ Se agotaron los reintentos para actualizar el modal');
        }
    }
}

function debugModalElements() {
    /**
     * Función de debug para verificar el estado de los elementos del modal
     */
    console.log('🔍 DEBUG: Estado de elementos del modal');

    const fileDisplaySection = document.getElementById('exam-file-display');
    const documentsSection = document.getElementById('exam-documents-summary');

    if (fileDisplaySection) {
        console.log('📎 Sección de archivos adjuntos encontrada');
        console.log('📏 Contenido HTML (primeros 100 chars):', fileDisplaySection.innerHTML.substring(0, 100));
    } else {
        console.error('❌ Sección exam-file-display NO encontrada');
    }

    if (documentsSection) {
        console.log('📁 Sección de documentos encontrada');
        console.log('📏 Contenido HTML (primeros 100 chars):', documentsSection.innerHTML.substring(0, 100));

        // Buscar badges de documentos
        const badges = documentsSection.querySelectorAll('.badge');
        console.log('🏷️ Badges encontrados:', badges.length);
        badges.forEach((badge, index) => {
            console.log(`   Badge ${index + 1}: ${badge.textContent.trim()}`);
        });

        // Verificar si se actualizó correctamente
        const totalText = documentsSection.textContent;
        if (totalText.includes('documento total') || totalText.includes('documentos total')) {
            const match = totalText.match(/(\d+)\s+documentos?\s+total/);
            if (match) {
                const documentCount = parseInt(match[1]);
                console.log(`📊 Documentos mostrados en UI: ${documentCount}`);
                return documentCount;
            }
        }
    } else {
        console.error('❌ Sección exam-documents-summary NO encontrada');
    }

    // Verificar si el modal está visible
    const modal = document.querySelector('.modal.show');
    if (modal) {
        console.log('👁️ Modal visible encontrado');
    } else {
        console.warn('⚠️ No se encontró modal visible');
    }

    return 0;
}

function verifyDocumentsUpdate(expectedCount = null) {
    /**
     * Verifica que la sección de documentos se haya actualizado correctamente
     */
    const documentsSection = document.getElementById('exam-documents-summary');
    if (!documentsSection) return false;

    const totalText = documentsSection.textContent;
    const match = totalText.match(/(\d+)\s+documentos?\s+total/);

    if (match) {
        const actualCount = parseInt(match[1]);
        console.log(`✅ Verificación: ${actualCount} documentos mostrados`);

        if (expectedCount && actualCount >= expectedCount) {
            showNotification(`📋 Documentos actualizados: ${actualCount} archivo${actualCount > 1 ? 's' : ''} total`, 'info');
            return true;
        }
        return actualCount > 0;
    }

    return false;
}

async function uploadMultipleExamFiles(examId) {
    const fileInput = document.getElementById('exam-files');
    const files = fileInput.files;

    if (!files || files.length === 0) {
        showNotification('Por favor selecciona al menos un archivo', 'error');
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    // Validar archivos
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'dcm', 'dicom', 'doc', 'docx', 'txt'];

    for (let file of files) {
        if (file.size > maxSize) {
            showNotification(`El archivo "${file.name}" es demasiado grande (máx. 16MB)`, 'error');
            return;
        }

        const fileExt = file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExt)) {
            showNotification(`Tipo de archivo no permitido: "${file.name}"`, 'error');
            return;
        }
    }

    try {
        showNotification(`📤 Subiendo ${files.length} archivo${files.length > 1 ? 's' : ''}...`, 'info');

        let uploadedFiles = [];
        let errors = [];

        // Subir archivos uno por uno
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('exam_id', examId);

            try {
                const response = await fetch(`/api/patient/${userId}/exams/upload`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    uploadedFiles.push({
                        name: file.name,
                        url: data.file_url
                    });
                    console.log(`✅ Archivo subido: ${file.name} -> ${data.file_url}`);
                    console.log(`📋 URLs actualizadas: ${data.all_file_urls}`);
                } else {
                    errors.push(`${file.name}: ${data.error || 'Error desconocido'}`);
                    console.error(`❌ Error subiendo ${file.name}:`, data.error);
                }
            } catch (error) {
                errors.push(`${file.name}: Error de conexión`);
            }
        }

        // Mostrar resultados
        if (uploadedFiles.length > 0) {
            showNotification(`✅ ${uploadedFiles.length} archivo${uploadedFiles.length > 1 ? 's subidos' : ' subido'} exitosamente`, 'success');

            // Actualizar inmediatamente sin delay
            console.log('🔄 Actualizando modal inmediatamente después de subir archivos...');
            updateExamModalFiles(examId);

            // Forzar actualización adicional después de un delay más largo
            setTimeout(() => {
                console.log('🔄 Forzando segunda actualización del modal...');
                updateExamModalFiles(examId);
            }, 1000);

            // También recargar la lista de exámenes con un pequeño delay
            setTimeout(() => {
                console.log('🔄 Recargando lista de exámenes...');
                loadExams();
            }, 200);
        }

        if (errors.length > 0) {
            showNotification(`⚠️ Errores en ${errors.length} archivo${errors.length > 1 ? 's' : ''}`, 'error');
            console.error('Errores de subida:', errors);
        }

        // Limpiar selección
        clearFileSelection();

    } catch (error) {
        console.error('Error subiendo archivos:', error);
        showNotification('Error de conexión al subir archivos', 'error');
    }
}

// Mantener función original para compatibilidad
async function uploadExamFile(examId) {
    const fileInput = document.getElementById('exam-file') || document.getElementById('exam-files');
    const file = fileInput.files[0];

    if (!file) {
        showNotification('Por favor selecciona un archivo', 'error');
        return;
    }

    const userId = getCurrentUserId();
    if (!userId) {
        showNotification('Error: No se pudo identificar al usuario', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('exam_id', examId);

    try {
        showNotification('📤 Subiendo archivo...', 'info');

        const response = await fetch(`/api/patient/${userId}/exams/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showNotification('✅ Archivo subido exitosamente', 'success');

            // Actualizar la vista previa
            const fileDisplay = document.getElementById('exam-file-display');
            if (fileDisplay) {
                fileDisplay.innerHTML = `
                    <div class="file-preview">
                        ${getFilePreview(data.file_url)}
                        <div class="file-actions mt-2">
                            <button class="btn btn-sm btn-primary" onclick="openFile('${data.file_url}')">
                                <i class="fas fa-external-link-alt me-1"></i>Abrir
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="downloadFile('${data.file_url}')">
                                <i class="fas fa-download me-1"></i>Descargar
                            </button>
                        </div>
                    </div>
                `;
            }

            // Limpiar el input
            fileInput.value = '';

            // Recargar la lista de exámenes
            setTimeout(() => {
                loadExams();
            }, 1000);
        } else {
            showNotification(data.error || 'Error subiendo archivo', 'error');
        }
    } catch (error) {
        console.error('Error subiendo archivo:', error);
        showNotification('Error de conexión al subir archivo', 'error');
    }
}

function printExam(examId) {
    showNotification('🖨️ Función de impresión en desarrollo', 'info');
    // TODO: Implementar función de impresión
}

// === SISTEMA DE DIÁLOGOS PERSONALIZADOS ===

function showCustomConfirm(title, message, warning) {
    // Crear el modal
    const modal = document.createElement('div');
    modal.className = 'custom-confirm-modal';
    modal.innerHTML = `
        <div class="custom-confirm-overlay">
            <div class="custom-confirm-dialog">
                <div class="custom-confirm-header">
                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                    <h5 class="mb-0">${title}</h5>
                </div>
                <div class="custom-confirm-body">
                    <p class="mb-2 fw-medium">${message}</p>
                    <p class="text-muted small mb-0">${warning}</p>
                </div>
                <div class="custom-confirm-footer">
                    <button class="btn btn-secondary me-2" id="confirm-cancel">
                        <i class="fas fa-times me-1"></i>Cancelar
                    </button>
                    <button class="btn btn-danger" id="confirm-delete">
                        <i class="fas fa-trash me-1"></i>Eliminar
                    </button>
                </div>
            </div>
        </div>
    `;

    // Agregar estilos
    const style = document.createElement('style');
    style.textContent = `
        .custom-confirm-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .custom-confirm-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.2s ease-out;
        }
        
        .custom-confirm-dialog {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 90%;
            overflow: hidden;
            animation: slideIn 0.3s ease-out;
        }
        
        .custom-confirm-header {
            padding: 20px 24px 16px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            background: #f8f9fa;
        }
        
        .custom-confirm-body {
            padding: 20px 24px;
        }
        
        .custom-confirm-footer {
            padding: 16px 24px 20px;
            display: flex;
            justify-content: flex-end;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { 
                opacity: 0;
                transform: translateY(-20px) scale(0.95);
            }
            to { 
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .custom-confirm-dialog .btn {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .custom-confirm-dialog .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
    `;

    // Función para limpiar el modal
    const cleanup = () => {
        if (document.body.contains(modal)) {
            document.body.removeChild(modal);
        }
        if (document.head.contains(style)) {
            document.head.removeChild(style);
        }
        document.removeEventListener('keydown', handleEscape);
    };

    // Manejar escape
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            cleanup();
        }
    };

    // Agregar al DOM
    document.head.appendChild(style);
    document.body.appendChild(modal);
    document.addEventListener('keydown', handleEscape);

    // Configurar eventos
    const cancelBtn = modal.querySelector('#confirm-cancel');
    const deleteBtn = modal.querySelector('#confirm-delete');
    const overlay = modal.querySelector('.custom-confirm-overlay');

    // Crear una promesa que se resuelve cuando el usuario hace clic
    return new Promise((resolve) => {
        cancelBtn.addEventListener('click', () => {
            cleanup();
            resolve(false);
        });

        deleteBtn.addEventListener('click', () => {
            cleanup();
            resolve(true);
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                cleanup();
                resolve(false);
            }
        });
    });
}


