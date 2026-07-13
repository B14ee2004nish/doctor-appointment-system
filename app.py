"""
app.py - Main Flask application entry point
"""

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os

from config import DevelopmentConfig, ProductionConfig
from models import db, User, Doctor, AvailableSlot
from routes import register_routes

# Create Flask app
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# app = Flask(__name__, 
#             template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
#             static_folder=os.path.join(BASE_DIR, 'frontend', 'static'))


# Load configuration
app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

# Register all routes
register_routes(app)

# ============================================
# CREATE SAMPLE DATA FUNCTION
# ============================================

def create_sample_data():
    """Create sample data for testing"""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin',
        phone='555-0000'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create sample patients
    patients = [
        User(username='patient1', email='patient1@email.com', phone='555-0101', role='patient'),
        User(username='patient2', email='patient2@email.com', phone='555-0102', role='patient'),
        User(username='patient3', email='patient3@email.com', phone='555-0103', role='patient'),
    ]
    for patient in patients:
        patient.set_password('patient123')
        db.session.add(patient)
    
    db.session.commit()
    
    # Create sample doctors
    doctors_data = [
        {'name': 'Dr. Sarah Smith', 'specialty': 'Cardiology', 'phone': '555-1001', 'email': 'sarah.smith@hospital.com', 'bio': 'Cardiologist with 15 years of experience', 'experience': 15},
        {'name': 'Dr. Michael Johnson', 'specialty': 'Dermatology', 'phone': '555-1002', 'email': 'michael.johnson@hospital.com', 'bio': 'Dermatologist specializing in skin cancer', 'experience': 12},
        {'name': 'Dr. Emily Williams', 'specialty': 'Orthopedics', 'phone': '555-1003', 'email': 'emily.williams@hospital.com', 'bio': 'Orthopedic surgeon specializing in sports injuries', 'experience': 10},
        {'name': 'Dr. David Brown', 'specialty': 'Pediatrics', 'phone': '555-1004', 'email': 'david.brown@hospital.com', 'bio': 'Pediatrician with 8 years of experience', 'experience': 8},
        {'name': 'Dr. Lisa Davis', 'specialty': 'Neurology', 'phone': '555-1005', 'email': 'lisa.davis@hospital.com', 'bio': 'Neurologist specializing in stroke care', 'experience': 14},
    ]
    
    for doc_data in doctors_data:
        doctor = Doctor(**doc_data)
        db.session.add(doctor)
    
    db.session.commit()
    
    # Create available slots for each doctor
    today = datetime.now().date()
    for doctor in Doctor.query.all():
        for i in range(7):  # Next 7 days
            date = today + timedelta(days=i)
            if date.weekday() < 5:  # Weekdays only
                date_str = date.strftime('%Y-%m-%d')
                # Morning and afternoon slots
                for time in ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']:
                    slot = AvailableSlot(
                        doctor_id=doctor.id,
                        date=date_str,
                        time=time,
                        is_booked=False
                    )
                    db.session.add(slot)
    
    db.session.commit()
    print("✓ Sample data created successfully!")

# ============================================
# CREATE TABLES AND SAMPLE DATA (RUNS AT STARTUP)
# ============================================

with app.app_context():
    db.create_all()
    if Doctor.query.count() == 0:
        create_sample_data()

# ============================================
# RUN THE APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)