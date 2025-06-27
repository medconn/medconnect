import React from 'react';

const ServiceHistory = ({ services }) => {
    // Función para determinar el color de fondo del avatar basado en el nombre del paciente
    const getAvatarColor = (name) => {
        const colors = [
            '#4299e1', // blue
            '#48bb78', // green
            '#ed8936', // orange
            '#9f7aea', // purple
            '#f56565', // red
            '#38b2ac', // teal
        ];

        // Usar la primera letra del nombre para seleccionar un color
        const index = name.charCodeAt(0) % colors.length;
        return colors[index];
    };

    // Función para obtener las iniciales del nombre
    const getInitials = (name) => {
        return name
            .split(' ')
            .map(n => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    };

    // Función para renderizar estrellas de calificación
    const renderStars = (rating) => {
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;

        // Estrellas completas
        for (let i = 0; i < fullStars; i++) {
            stars.push(
                <svg key={`full-${i}`} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
            );
        }

        // Estrella media si es necesario
        if (hasHalfStar) {
            stars.push(
                <svg key="half" className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <defs>
                        <linearGradient id="half-star-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="50%" stopColor="currentColor" />
                            <stop offset="50%" stopColor="#e2e8f0" />
                        </linearGradient>
                    </defs>
                    <path fill="url(#half-star-gradient)" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
            );
        }

        // Estrellas vacías
        const emptyStars = 5 - stars.length;
        for (let i = 0; i < emptyStars; i++) {
            stars.push(
                <svg key={`empty-${i}`} className="w-4 h-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
            );
        }

        return stars;
    };

    // Función para determinar la clase de badge basada en el estado
    const getStatusBadgeClass = (status) => {
        switch (status) {
            case 'Completado':
                return 'badge-success';
            case 'Programado':
                return 'badge-info';
            case 'Pendiente':
                return 'badge-warning';
            case 'Cancelado':
                return 'badge-danger';
            default:
                return 'badge-primary';
        }
    };

    return (
        <div className="dashboard-card">
            <div className="card-header">
                <h3 className="card-title">
                    <svg className="card-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Servicios Recientes
                </h3>
                <div className="card-actions">
                    <button className="action-btn">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
                        </svg>
                    </button>
                    <button className="action-btn">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <div className="service-history">
                {services.length === 0 ? (
                    <div className="p-4 text-center text-gray-500">
                        No hay servicios recientes para mostrar
                    </div>
                ) : (
                    <div>
                        {services.map((service, index) => (
                            <div
                                key={index}
                                className={`service-history-item ${index !== services.length - 1 ? 'border-b border-gray-200' : ''}`}
                            >
                                <div className="service-item-content">
                                    <div className="service-patient">
                                        {service.avatarUrl ? (
                                            <img
                                                src={service.avatarUrl}
                                                alt={service.patientName}
                                                className="patient-avatar-sm"
                                            />
                                        ) : (
                                            <div
                                                className="patient-avatar-sm"
                                                style={{ backgroundColor: getAvatarColor(service.patientName) }}
                                            >
                                                {getInitials(service.patientName)}
                                            </div>
                                        )}
                                        <div className="patient-info">
                                            <h4 className="patient-name">{service.patientName}</h4>
                                            <div className="service-details">
                                                <span className={`badge-${service.serviceType === 'Consulta' ? 'primary' : 'info'}`}>
                                                    {service.serviceType}
                                                </span>
                                                <span className="service-date">{service.date}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="service-meta">
                                        {service.rating > 0 && (
                                            <div className="service-rating">
                                                {renderStars(service.rating)}
                                            </div>
                                        )}
                                        <span className={`service-status ${getStatusBadgeClass(service.status)}`}>
                                            {service.status}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="card-footer">
                <button className="btn-sm btn-outline-secondary full-width">
                    Ver todos los servicios
                </button>
            </div>
        </div>
    );
};

export default ServiceHistory; 