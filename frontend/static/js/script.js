/**
 * script.js - Custom JavaScript for Doctor Appointment System
 */

// ============================================
// FORM VALIDATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Add validation to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
            }
        });
    });
});

// ============================================
// DATE VALIDATION
// ============================================

function validateDate(dateInput) {
    const selected = new Date(dateInput.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (selected < today) {
        alert('Please select a future date.');
        dateInput.value = '';
        return false;
    }
    return true;
}

// ============================================
// APPOINTMENT MANAGEMENT
// ============================================

function cancelAppointment(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        window.location.href = `/cancel-appointment/${appointmentId}`;
    }
}

function completeAppointment(appointmentId) {
    if (confirm('Mark this appointment as completed?')) {
        window.location.href = `/admin/complete/${appointmentId}`;
    }
}

// ============================================
// DOCTOR SEARCH
// ============================================

function filterDoctors() {
    const searchInput = document.getElementById('doctorSearch');
    const searchTerm = searchInput.value.toLowerCase();
    const doctorCards = document.querySelectorAll('.doctor-card');
    
    doctorCards.forEach(card => {
        const name = card.dataset.name.toLowerCase();
        const specialty = card.dataset.specialty.toLowerCase();
        
        if (name.includes(searchTerm) || specialty.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// ============================================
// SLOT SELECTION
// ============================================

function selectSlot(element) {
    // Remove active class from all slots
    document.querySelectorAll('.slot-btn').forEach(btn => {
        btn.classList.remove('active', 'btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    // Add active class to selected slot
    element.classList.remove('btn-outline-primary');
    element.classList.add('active', 'btn-primary');
    
    // Update hidden input
    document.getElementById('selectedSlot').value = element.dataset.slotId;
}

// ============================================
// LOAD SLOTS VIA AJAX
// ============================================

async function loadSlots(doctorId, date) {
    if (!doctorId || !date) {
        document.getElementById('slotsContainer').innerHTML = 
            '<p class="text-muted">Select a doctor and date to see available slots</p>';
        return;
    }
    
    try {
        const response = await fetch(`/get_available_slots?doctor_id=${doctorId}&date=${date}`);
        const slots = await response.json();
        
        const container = document.getElementById('slotsContainer');
        
        if (Object.keys(slots).length === 0) {
            container.innerHTML = '<p class="text-warning">No slots available for this date</p>';
            return;
        }
        
        let html = '';
        for (const [date, times] of Object.entries(slots)) {
            html += `<div class="w-100"><strong>${date}</strong></div>`;
            times.forEach(slot => {
                html += `
                    <div class="slot-btn btn btn-outline-primary" 
                         data-slot-id="${slot.id}"
                         onclick="selectSlot(this)">
                        ${slot.time}
                    </div>
                `;
            });
        }
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading slots:', error);
        document.getElementById('slotsContainer').innerHTML = 
            '<p class="text-danger">Error loading slots. Please try again.</p>';
    }
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container.mt-3');
    if (container) {
        container.prepend(alertDiv);
    }
}

// ============================================
// DASHBOARD CHARTS (using Chart.js if available)
// ============================================

function initDashboardCharts() {
    const ctx = document.getElementById('appointmentChart');
    if (!ctx) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Scheduled', 'Completed', 'Cancelled'],
            datasets: [{
                data: [12, 19, 3],
                backgroundColor: ['#0d6efd', '#198754', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(timeStr) {
    const [hours, minutes] = timeStr.split(':');
    const h = parseInt(hours);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    return `${h12}:${minutes} ${ampm}`;
}

function getStatusBadge(status) {
    const classes = {
        'Scheduled': 'bg-success',
        'Completed': 'bg-info',
        'Cancelled': 'bg-danger',
        'No-Show': 'bg-warning'
    };
    return `<span class="badge ${classes[status] || 'bg-secondary'}">${status}</span>`;
}

// ============================================
// AUTO-REFRESH FOR AVAILABLE SLOTS
// ============================================

function refreshSlots() {
    const doctorId = document.getElementById('doctor_id')?.value;
    const date = document.getElementById('date')?.value;
    if (doctorId && date) {
        loadSlots(doctorId, date);
    }
}

// Refresh slots every 30 seconds if on booking page
if (document.getElementById('bookingForm')) {
    setInterval(refreshSlots, 30000);
}