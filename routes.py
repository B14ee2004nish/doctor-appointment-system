# """
# routes.py - All URL routes and API endpoints
# """

# from flask import render_template, request, jsonify, redirect, url_for, flash, session
# from flask_login import login_user, logout_user, login_required, current_user
# from datetime import datetime, timedelta
# import json

# from models import db, User, Doctor, AvailableSlot, Appointment

# def register_routes(app):
#     """Register all routes with the Flask app"""
    
#     # ============================================
#     # PUBLIC ROUTES
#     # ============================================
    
#     @app.route('/')
#     def index():
#         """Homepage"""
#         doctors = Doctor.query.limit(6).all()
#         return render_template('index.html', doctors=doctors)
    
#     @app.route('/doctors')
#     def doctors():
#         """View all doctors"""
#         search = request.args.get('search', '')
#         if search:
#             doctors = Doctor.query.filter(
#                 (Doctor.name.contains(search)) | 
#                 (Doctor.specialty.contains(search))
#             ).all()
#         else:
#             doctors = Doctor.query.all()
#         return render_template('doctors.html', doctors=doctors, search=search)
    
#     @app.route('/doctor/<int:doctor_id>')
#     def doctor_detail(doctor_id):
#         """View doctor details and available slots"""
#         doctor = Doctor.query.get_or_404(doctor_id)
#         slots = AvailableSlot.query.filter_by(
#             doctor_id=doctor_id, 
#             is_booked=False
#         ).order_by(AvailableSlot.date, AvailableSlot.time).all()
#         return render_template('doctor_detail.html', doctor=doctor, slots=slots)
    
#     @app.route('/get_available_slots')
#     def get_available_slots():
#         """API endpoint to get available slots for a doctor"""
#         doctor_id = request.args.get('doctor_id')
#         date = request.args.get('date')
        
#         if not doctor_id:
#             return jsonify({'error': 'Doctor ID required'}), 400
        
#         query = AvailableSlot.query.filter_by(doctor_id=doctor_id, is_booked=False)
#         if date:
#             query = query.filter_by(date=date)
        
#         slots = query.order_by(AvailableSlot.date, AvailableSlot.time).all()
        
#         # Group slots by date
#         slots_by_date = {}
#         for slot in slots:
#             if slot.date not in slots_by_date:
#                 slots_by_date[slot.date] = []
#             slots_by_date[slot.date].append({
#                 'id': slot.id,
#                 'time': slot.time
#             })
        
#         return jsonify(slots_by_date)
    
#     # ============================================
#     # AUTHENTICATION ROUTES
#     # ============================================
    
#     @app.route('/register', methods=['GET', 'POST'])
#     def register():
#         """User registration"""
#         if request.method == 'POST':
#             username = request.form.get('username')
#             email = request.form.get('email')
#             password = request.form.get('password')
#             phone = request.form.get('phone')
            
#             # Check if user exists
#             if User.query.filter_by(username=username).first():
#                 flash('Username already exists!', 'danger')
#                 return render_template('register.html')
            
#             if User.query.filter_by(email=email).first():
#                 flash('Email already registered!', 'danger')
#                 return render_template('register.html')
            
#             # Create new user
#             user = User(username=username, email=email, phone=phone)
#             user.set_password(password)
            
#             db.session.add(user)
#             db.session.commit()
            
#             flash('Registration successful! Please login.', 'success')
#             return redirect(url_for('login'))
        
#         return render_template('register.html')
    
#     @app.route('/login', methods=['GET', 'POST'])
#     def login():
#         """User login"""
#         if request.method == 'POST':
#             username = request.form.get('username')
#             password = request.form.get('password')
            
#             user = User.query.filter_by(username=username).first()
            
#             if user and user.check_password(password):
#                 login_user(user)
#                 flash('Login successful!', 'success')
                
#                 # Redirect based on role
#                 if user.role == 'admin':
#                     return redirect(url_for('admin_dashboard'))
#                 else:
#                     return redirect(url_for('dashboard'))
#             else:
#                 flash('Invalid username or password!', 'danger')
        
#         return render_template('login.html')
    
#     @app.route('/logout')
#     @login_required
#     def logout():
#         """User logout"""
#         logout_user()
#         flash('Logged out successfully!', 'info')
#         return redirect(url_for('index'))
    
#     # ============================================
#     # PATIENT ROUTES (Logged in users)
#     # ============================================
    
#     @app.route('/dashboard')
#     @login_required
#     def dashboard():
#         """User dashboard"""
#         # Get upcoming appointments
#         today = datetime.now().strftime('%Y-%m-%d')
#         upcoming = Appointment.query.filter_by(
#             patient_id=current_user.id,
#             status='Scheduled'
#         ).filter(Appointment.date >= today).order_by(
#             Appointment.date, Appointment.time
#         ).limit(5).all()
        
#         # Get appointment count
#         total = Appointment.query.filter_by(patient_id=current_user.id).count()
#         completed = Appointment.query.filter_by(
#             patient_id=current_user.id,
#             status='Completed'
#         ).count()
#         cancelled = Appointment.query.filter_by(
#             patient_id=current_user.id,
#             status='Cancelled'
#         ).count()
        
#         return render_template('dashboard.html', 
#                              upcoming=upcoming,
#                              total=total,
#                              completed=completed,
#                              cancelled=cancelled)
    
#     @app.route('/book', methods=['GET', 'POST'])
#     @login_required
#     def book_appointment():
#         """Book an appointment"""
#         if request.method == 'POST':
#             doctor_id = request.form.get('doctor_id')
#             slot_id = request.form.get('slot_id')
#             reason = request.form.get('reason')
            
#             # Get slot
#             slot = AvailableSlot.query.get(slot_id)
#             if not slot or slot.is_booked:
#                 flash('This slot is no longer available!', 'danger')
#                 return redirect(url_for('book_appointment'))
            
#             # Create appointment
#             appointment = Appointment(
#                 doctor_id=doctor_id,
#                 patient_id=current_user.id,
#                 slot_id=slot_id,
#                 date=slot.date,
#                 time=slot.time,
#                 reason=reason,
#                 status='Scheduled'
#             )
            
#             # Mark slot as booked
#             slot.is_booked = True
            
#             db.session.add(appointment)
#             db.session.commit()
            
#             flash('Appointment booked successfully!', 'success')
#             return redirect(url_for('my_appointments'))
        
#         # GET request - show booking form
#         doctors = Doctor.query.filter_by(is_available=True).all()
#         return render_template('book.html', doctors=doctors)
    
#     @app.route('/my-appointments')
#     @login_required
#     def my_appointments():
#         """View user's appointments"""
#         appointments = Appointment.query.filter_by(
#             patient_id=current_user.id
#         ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        
#         return render_template('appointments.html', appointments=appointments)
    
#     @app.route('/cancel-appointment/<int:appointment_id>')
#     @login_required
#     def cancel_appointment(appointment_id):
#         """Cancel an appointment"""
#         appointment = Appointment.query.get_or_404(appointment_id)
        
#         # Check if this belongs to current user
#         if appointment.patient_id != current_user.id:
#             flash('Unauthorized!', 'danger')
#             return redirect(url_for('my_appointments'))
        
#         if appointment.status == 'Scheduled':
#             appointment.status = 'Cancelled'
            
#             # Free up the slot
#             slot = AvailableSlot.query.get(appointment.slot_id)
#             if slot:
#                 slot.is_booked = False
            
#             db.session.commit()
#             flash('Appointment cancelled successfully!', 'success')
#         else:
#             flash('Cannot cancel this appointment.', 'warning')
        
#         return redirect(url_for('my_appointments'))
    
#     # ============================================
#     # ADMIN ROUTES
#     # ============================================
    
#     @app.route('/admin')
#     @login_required
#     def admin_dashboard():
#         """Admin dashboard"""
#         if current_user.role != 'admin':
#             flash('Admin access required!', 'danger')
#             return redirect(url_for('dashboard'))
        
#         # Statistics
#         total_patients = User.query.filter_by(role='patient').count()
#         total_doctors = Doctor.query.count()
#         total_appointments = Appointment.query.count()
#         today = datetime.now().strftime('%Y-%m-%d')
#         today_appointments = Appointment.query.filter_by(date=today).count()
        
#         # Recent appointments
#         recent = Appointment.query.order_by(
#             Appointment.created_at.desc()
#         ).limit(10).all()
        
#         # Get all doctors for the slots dropdown
#         doctors = Doctor.query.all()
        
#         return render_template('admin.html', 
#                              total_patients=total_patients,
#                              total_doctors=total_doctors,
#                              total_appointments=total_appointments,
#                              today_appointments=today_appointments,
#                              recent=recent,
#                              doctors=doctors)
    
#     @app.route('/admin/doctors')
#     @login_required
#     def admin_doctors():
#         """Admin - manage doctors"""
#         if current_user.role != 'admin':
#             flash('Admin access required!', 'danger')
#             return redirect(url_for('dashboard'))
        
#         doctors = Doctor.query.all()
#         return render_template('admin_doctors.html', doctors=doctors)
    
#     @app.route('/admin/doctors/add', methods=['POST'])
#     @login_required
#     def add_doctor():
#         """Admin - add new doctor"""
#         if current_user.role != 'admin':
#             return jsonify({'error': 'Unauthorized'}), 403
        
#         try:
#             data = request.get_json()
            
#             if not data:
#                 return jsonify({'error': 'No data received'}), 400
            
#             name = data.get('name', '').strip()
#             specialty = data.get('specialty', '').strip()
            
#             if not name or not specialty:
#                 return jsonify({'error': 'Name and specialty are required'}), 400
            
#             doctor = Doctor(
#                 name=name,
#                 specialty=specialty,
#                 phone=data.get('phone', ''),
#                 email=data.get('email', ''),
#                 bio=data.get('bio', ''),
#                 experience=int(data.get('experience', 0)),
#                 is_available=True
#             )
            
#             db.session.add(doctor)
#             db.session.commit()
            
#             return jsonify({
#                 'success': True,
#                 'message': f'Dr. {name} added successfully!',
#                 'id': doctor.id
#             })
            
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500
    
#     @app.route('/admin/slots/add', methods=['POST'])
#     @login_required
#     def add_slots():
#         """Admin - add available slots for a doctor"""
#         if current_user.role != 'admin':
#             return jsonify({'error': 'Unauthorized'}), 403
        
#         try:
#             data = request.get_json()
            
#             if not data:
#                 return jsonify({'error': 'No data received'}), 400
            
#             doctor_id = data.get('doctor_id')
#             date = data.get('date')
#             times = data.get('times', [])
            
#             if not doctor_id or not date or not times:
#                 return jsonify({'error': 'Doctor ID, date, and times are required'}), 400
            
#             # Check if doctor exists
#             doctor = Doctor.query.get(doctor_id)
#             if not doctor:
#                 return jsonify({'error': 'Doctor not found'}), 404
            
#             # Add each time slot
#             added_count = 0
#             for time in times:
#                 # Check if slot already exists
#                 existing = AvailableSlot.query.filter_by(
#                     doctor_id=doctor_id,
#                     date=date,
#                     time=time
#                 ).first()
                
#                 if not existing:
#                     slot = AvailableSlot(
#                         doctor_id=doctor_id,
#                         date=date,
#                         time=time,
#                         is_booked=False
#                     )
#                     db.session.add(slot)
#                     added_count += 1
            
#             db.session.commit()
            
#             return jsonify({
#                 'success': True,
#                 'message': f'{added_count} slots added successfully!',
#                 'added_count': added_count
#             })
            
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'error': str(e)}), 500
    
#     @app.route('/admin/complete/<int:appointment_id>')
#     @login_required
#     def complete_appointment(appointment_id):
#         """Admin - mark appointment as completed"""
#         if current_user.role != 'admin':
#             flash('Admin access required!', 'danger')
#             return redirect(url_for('dashboard'))
        
#         appointment = Appointment.query.get_or_404(appointment_id)
#         appointment.status = 'Completed'
#         db.session.commit()
        
#         flash('Appointment marked as completed!', 'success')
#         return redirect(url_for('admin_dashboard'))
    
#     # ============================================
#     # API ROUTES (for AJAX calls)
#     # ============================================
    
#     @app.route('/api/doctors')
#     def api_doctors():
#         """API - Get all doctors"""
#         doctors = Doctor.query.all()
#         return jsonify([{
#             'id': d.id,
#             'name': d.name,
#             'specialty': d.specialty,
#             'phone': d.phone,
#             'email': d.email,
#             'rating': d.rating
#         } for d in doctors])
    
#     @app.route('/api/appointments')
#     @login_required
#     def api_appointments():
#         """API - Get user's appointments"""
#         appointments = Appointment.query.filter_by(
#             patient_id=current_user.id
#         ).all()
        
#         return jsonify([{
#             'id': a.id,
#             'doctor': a.doctor.name,
#             'date': a.date,
#             'time': a.time,
#             'status': a.status
#         } for a in appointments])
    
#     @app.route('/api/check-slot/<int:slot_id>')
#     def api_check_slot(slot_id):
#         """API - Check if a slot is still available"""
#         slot = AvailableSlot.query.get(slot_id)
#         if not slot:
#             return jsonify({'available': False, 'error': 'Slot not found'})
        
#         return jsonify({
#             'available': not slot.is_booked,
#             'date': slot.date,
#             'time': slot.time
#         })


"""
routes.py - All URL routes and API endpoints
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import json

from models import db, User, Doctor, AvailableSlot, Appointment

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # ============================================
    # PUBLIC ROUTES
    # ============================================
    
    @app.route('/')
    def index():
        """Homepage"""
        doctors = Doctor.query.limit(6).all()
        return render_template('index.html', doctors=doctors)
    
    @app.route('/doctors')
    def doctors():
        """View all doctors"""
        search = request.args.get('search', '')
        if search:
            doctors = Doctor.query.filter(
                (Doctor.name.contains(search)) | 
                (Doctor.specialty.contains(search))
            ).all()
        else:
            doctors = Doctor.query.all()
        return render_template('doctors.html', doctors=doctors, search=search)
    
    @app.route('/doctor/<int:doctor_id>')
    def doctor_detail(doctor_id):
        """View doctor details and available slots"""
        doctor = Doctor.query.get_or_404(doctor_id)
        slots = AvailableSlot.query.filter_by(
            doctor_id=doctor_id, 
            is_booked=False
        ).order_by(AvailableSlot.date, AvailableSlot.time).all()
        return render_template('doctor_detail.html', doctor=doctor, slots=slots)
    
    @app.route('/get_available_slots')
    def get_available_slots():
        """API endpoint to get available slots for a doctor"""
        doctor_id = request.args.get('doctor_id')
        date = request.args.get('date')
        
        if not doctor_id:
            return jsonify({'error': 'Doctor ID required'}), 400
        
        query = AvailableSlot.query.filter_by(doctor_id=doctor_id, is_booked=False)
        if date:
            query = query.filter_by(date=date)
        
        slots = query.order_by(AvailableSlot.date, AvailableSlot.time).all()
        
        slots_by_date = {}
        for slot in slots:
            if slot.date not in slots_by_date:
                slots_by_date[slot.date] = []
            slots_by_date[slot.date].append({
                'id': slot.id,
                'time': slot.time
            })
        
        return jsonify(slots_by_date)
    
    # ============================================
    # AUTHENTICATION ROUTES
    # ============================================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists!', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'danger')
                return render_template('register.html')
            
            user = User(username=username, email=email, phone=phone)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('Logged out successfully!', 'info')
        return redirect(url_for('index'))
    
    # ============================================
    # PATIENT ROUTES
    # ============================================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Patient dashboard - shows ONLY this patient's appointments"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get ONLY this patient's appointments
        upcoming = Appointment.query.filter_by(
            patient_id=current_user.id,
            status='Scheduled'
        ).filter(Appointment.date >= today).order_by(
            Appointment.date, Appointment.time
        ).all()
        
        total = Appointment.query.filter_by(patient_id=current_user.id).count()
        completed = Appointment.query.filter_by(
            patient_id=current_user.id,
            status='Completed'
        ).count()
        cancelled = Appointment.query.filter_by(
            patient_id=current_user.id,
            status='Cancelled'
        ).count()
        
        return render_template('dashboard.html', 
                             upcoming=upcoming,
                             total=total,
                             completed=completed,
                             cancelled=cancelled)
    
    @app.route('/book', methods=['GET', 'POST'])
    @login_required
    def book_appointment():
        """Book an appointment"""
        if request.method == 'POST':
            doctor_id = request.form.get('doctor_id')
            slot_id = request.form.get('slot_id')
            reason = request.form.get('reason')
            
            if not doctor_id or not slot_id:
                flash('Please select a doctor and time slot.', 'danger')
                return redirect(url_for('book_appointment'))
            
            slot = AvailableSlot.query.get(slot_id)
            if not slot or slot.is_booked:
                flash('This slot is no longer available!', 'danger')
                return redirect(url_for('book_appointment'))
            
            # Create appointment
            appointment = Appointment(
                doctor_id=doctor_id,
                patient_id=current_user.id,
                slot_id=slot_id,
                date=slot.date,
                time=slot.time,
                reason=reason,
                status='Scheduled'
            )
            
            # Mark slot as booked
            slot.is_booked = True
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('✅ Appointment booked successfully!', 'success')
            return redirect(url_for('my_appointments'))
        
        doctors = Doctor.query.filter_by(is_available=True).all()
        return render_template('book.html', doctors=doctors)
    
    @app.route('/my-appointments')
    @login_required
    def my_appointments():
        """View user's appointments"""
        appointments = Appointment.query.filter_by(
            patient_id=current_user.id
        ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        
        return render_template('appointments.html', appointments=appointments)
    
    @app.route('/cancel-appointment/<int:appointment_id>')
    @login_required
    def cancel_appointment(appointment_id):
        """Cancel an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.patient_id != current_user.id:
            flash('Unauthorized!', 'danger')
            return redirect(url_for('my_appointments'))
        
        if appointment.status == 'Scheduled':
            appointment.status = 'Cancelled'
            
            slot = AvailableSlot.query.get(appointment.slot_id)
            if slot:
                slot.is_booked = False
            
            db.session.commit()
            flash('Appointment cancelled successfully!', 'success')
        else:
            flash('Cannot cancel this appointment.', 'warning')
        
        return redirect(url_for('my_appointments'))
    
    # ============================================
    # ADMIN ROUTES
    # ============================================
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin dashboard - shows ALL appointments"""
        if current_user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Statistics - ALL appointments
        total_patients = User.query.filter_by(role='patient').count()
        total_doctors = Doctor.query.count()
        total_appointments = Appointment.query.count()  # ← ALL appointments
        today = datetime.now().strftime('%Y-%m-%d')
        today_appointments = Appointment.query.filter_by(date=today).count()
        
        # Recent appointments - ALL appointments
        recent = Appointment.query.order_by(
            Appointment.created_at.desc()
        ).limit(10).all()
        
        doctors = Doctor.query.all()
        
        return render_template('admin.html', 
                             total_patients=total_patients,
                             total_doctors=total_doctors,
                             total_appointments=total_appointments,
                             today_appointments=today_appointments,
                             recent=recent,
                             doctors=doctors)
    
    @app.route('/admin/doctors')
    @login_required
    def admin_doctors():
        """Admin - manage doctors"""
        if current_user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        
        doctors = Doctor.query.all()
        return render_template('admin_doctors.html', doctors=doctors)
    
    @app.route('/admin/doctors/add', methods=['POST'])
    @login_required
    def add_doctor():
        """Admin - add new doctor"""
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data received'}), 400
            
            name = data.get('name', '').strip()
            specialty = data.get('specialty', '').strip()
            
            if not name or not specialty:
                return jsonify({'error': 'Name and specialty are required'}), 400
            
            doctor = Doctor(
                name=name,
                specialty=specialty,
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                bio=data.get('bio', ''),
                experience=int(data.get('experience', 0)),
                is_available=True
            )
            
            db.session.add(doctor)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Dr. {name} added successfully!',
                'id': doctor.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/slots/add', methods=['POST'])
    @login_required
    def add_slots():
        """Admin - add available slots for a doctor"""
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data received'}), 400
            
            doctor_id = data.get('doctor_id')
            date = data.get('date')
            times = data.get('times', [])
            
            if not doctor_id or not date or not times:
                return jsonify({'error': 'Doctor ID, date, and times are required'}), 400
            
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            added_count = 0
            for time in times:
                existing = AvailableSlot.query.filter_by(
                    doctor_id=doctor_id,
                    date=date,
                    time=time
                ).first()
                
                if not existing:
                    slot = AvailableSlot(
                        doctor_id=doctor_id,
                        date=date,
                        time=time,
                        is_booked=False
                    )
                    db.session.add(slot)
                    added_count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{added_count} slots added successfully!',
                'added_count': added_count
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/complete/<int:appointment_id>')
    @login_required
    def complete_appointment(appointment_id):
        """Admin - mark appointment as completed"""
        if current_user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Completed'
        db.session.commit()
        
        flash('Appointment marked as completed!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # ============================================
    # API ROUTES
    # ============================================
    
    @app.route('/api/doctors')
    def api_doctors():
        """API - Get all doctors"""
        doctors = Doctor.query.all()
        return jsonify([{
            'id': d.id,
            'name': d.name,
            'specialty': d.specialty,
            'phone': d.phone,
            'email': d.email,
            'rating': d.rating
        } for d in doctors])
    
    @app.route('/api/appointments')
    @login_required
    def api_appointments():
        """API - Get user's appointments"""
        appointments = Appointment.query.filter_by(
            patient_id=current_user.id
        ).all()
        
        return jsonify([{
            'id': a.id,
            'doctor': a.doctor.name,
            'date': a.date,
            'time': a.time,
            'status': a.status
        } for a in appointments])
    
    @app.route('/api/check-slot/<int:slot_id>')
    def api_check_slot(slot_id):
        """API - Check if a slot is still available"""
        slot = AvailableSlot.query.get(slot_id)
        if not slot:
            return jsonify({'available': False, 'error': 'Slot not found'})
        
        return jsonify({
            'available': not slot.is_booked,
            'date': slot.date,
            'time': slot.time
        })