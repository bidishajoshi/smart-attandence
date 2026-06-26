"""
AttendanceAI - Student Routes
Student dashboard, face registration, attendance viewing.
"""
import os
import base64
import json
from datetime import datetime, date, timedelta
from flask import (render_template, redirect, url_for, flash,
                   request, jsonify, current_app, send_file)
from flask_login import login_required, current_user

from app import db
from app.models import (Student, AttendanceRecord, AttendanceStatus,
                         Class, Enrollment, FaceEmbedding, Notification)
from app.utils import role_required, log_action, face_engine, save_face_image
from . import student


def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        from app.models import UserRole
        if current_user.role != UserRole.STUDENT:
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated


@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard."""
    profile = current_user.student_profile
    if not profile:
        flash('Student profile not found.', 'error')
        return redirect(url_for('auth.logout'))
    
    today = date.today()
    
    # Today's attendance
    today_records = AttendanceRecord.query.filter_by(
        student_id=profile.id, date=today).all()
    
    # This month attendance
    first_day = today.replace(day=1)
    month_records = AttendanceRecord.query.filter(
        AttendanceRecord.student_id == profile.id,
        AttendanceRecord.date >= first_day
    ).all()
    
    month_present = sum(1 for r in month_records if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE])
    month_total = len(month_records)
    month_percentage = (month_present / month_total * 100) if month_total > 0 else 0
    
    # Per-class attendance
    enrolled_classes = Class.query.join(Enrollment).filter(
        Enrollment.student_id == profile.id,
        Enrollment.is_active == True
    ).all()
    
    class_stats = []
    for cls in enrolled_classes:
        cls_records = AttendanceRecord.query.filter_by(
            student_id=profile.id, class_id=cls.id).all()
        cls_total = len(cls_records)
        cls_present = sum(1 for r in cls_records if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE])
        cls_pct = (cls_present / cls_total * 100) if cls_total > 0 else 0
        class_stats.append({
            'class': cls,
            'total': cls_total,
            'present': cls_present,
            'percentage': round(cls_pct, 1),
            'alert': cls_pct < 75
        })
    
    # Recent notifications
    recent_notifications = current_user.notifications.order_by(
        db.desc(Notification.created_at)).limit(5).all()
    
    # Last 7 days for mini chart
    weekly_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        record = AttendanceRecord.query.filter_by(student_id=profile.id, date=day).first()
        weekly_data.append({
            'day': day.strftime('%a'),
            'status': record.status.value if record else 'no_class'
        })
    
    return render_template('student/dashboard.html',
                           profile=profile,
                           today_records=today_records,
                           month_present=month_present,
                           month_total=month_total,
                           month_percentage=round(month_percentage, 1),
                           overall_percentage=round(profile.attendance_percentage, 1),
                           class_stats=class_stats,
                           recent_notifications=recent_notifications,
                           weekly_data=weekly_data)


@student.route('/attendance')
@login_required
@student_required
def attendance():
    """Detailed attendance history."""
    profile = current_user.student_profile
    
    page = request.args.get('page', 1, type=int)
    class_filter = request.args.get('class_id', '')
    month_filter = request.args.get('month', '')
    status_filter = request.args.get('status', '')
    
    query = AttendanceRecord.query.filter_by(student_id=profile.id)
    
    if class_filter:
        query = query.filter_by(class_id=int(class_filter))
    if status_filter:
        query = query.filter_by(status=AttendanceStatus[status_filter.upper()])
    if month_filter:
        year, month = month_filter.split('-')
        first_day = date(int(year), int(month), 1)
        if int(month) == 12:
            last_day = date(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(int(year), int(month) + 1, 1) - timedelta(days=1)
        query = query.filter(
            AttendanceRecord.date >= first_day,
            AttendanceRecord.date <= last_day
        )
    
    records = query.order_by(AttendanceRecord.date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Get enrolled classes for filter
    classes = Class.query.join(Enrollment).filter(
        Enrollment.student_id == profile.id,
        Enrollment.is_active == True
    ).all()
    
    return render_template('student/attendance.html',
                           profile=profile, records=records, classes=classes,
                           class_filter=class_filter, month_filter=month_filter,
                           status_filter=status_filter)


@student.route('/face-registration')
@login_required
@student_required
def face_registration():
    """Face registration page."""
    profile = current_user.student_profile
    existing_embeddings = FaceEmbedding.query.filter_by(
        student_id=profile.id, is_active=True).all()
    max_images = current_app.config.get('MAX_FACE_IMAGES', 10)
    
    return render_template('student/face_registration.html',
                           profile=profile,
                           existing_count=len(existing_embeddings),
                           max_images=max_images)


@student.route('/face-registration/capture', methods=['POST'])
@login_required
@student_required
def capture_face():
    """Process captured face image."""
    profile = current_user.student_profile
    max_images = current_app.config.get('MAX_FACE_IMAGES', 10)
    
    existing_count = FaceEmbedding.query.filter_by(
        student_id=profile.id, is_active=True).count()
    
    if existing_count >= max_images:
        return jsonify({'success': False, 'message': f'Maximum {max_images} face images allowed'}), 400
    
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'success': False, 'message': 'No image data received'}), 400
    
    try:
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Save image
        upload_folder = current_app.config['UPLOAD_FOLDER']
        image_path = save_face_image(image_bytes, profile.id, upload_folder)
        full_path = os.path.join(upload_folder, image_path)
        
        # Validate face
        validation = face_engine.validate_face_image(full_path)
        if not validation['valid']:
            os.remove(full_path)
            return jsonify({'success': False, 'message': validation['message']}), 400
        
        # Extract encoding
        encoding = face_engine.extract_encoding_from_image(full_path)
        if not encoding:
            os.remove(full_path)
            return jsonify({'success': False, 'message': 'Could not extract face features'}), 400
        
        # Save to database
        embedding = FaceEmbedding(
            student_id=profile.id,
            image_path=image_path,
            confidence=0.95
        )
        embedding.set_embedding(encoding)
        db.session.add(embedding)
        
        # Update face registration status
        profile.face_registered = True
        db.session.commit()
        
        total = FaceEmbedding.query.filter_by(student_id=profile.id, is_active=True).count()
        log_action(db, 'FACE_REGISTERED', 'student', profile.id)
        
        return jsonify({
            'success': True,
            'message': 'Face captured successfully',
            'total_images': total,
            'max_images': max_images
        })
    
    except Exception as e:
        current_app.logger.error(f"Face capture error: {e}")
        return jsonify({'success': False, 'message': 'Failed to process image'}), 500


@student.route('/face-registration/delete/<int:embedding_id>', methods=['DELETE'])
@login_required
@student_required
def delete_face(embedding_id):
    """Delete a face embedding."""
    profile = current_user.student_profile
    embedding = FaceEmbedding.query.filter_by(
        id=embedding_id, student_id=profile.id).first_or_404()
    
    embedding.is_active = False
    
    # Check if any active embeddings remain
    remaining = FaceEmbedding.query.filter_by(
        student_id=profile.id, is_active=True).count()
    if remaining <= 1:
        profile.face_registered = remaining > 0
    
    db.session.commit()
    return jsonify({'success': True})


@student.route('/profile')
@login_required
@student_required
def profile():
    """Student profile page."""
    student_profile = current_user.student_profile
    return render_template('student/profile.html', profile=student_profile)


@student.route('/reports')
@login_required
@student_required
def reports():
    """Student reports."""
    profile = current_user.student_profile
    
    # Get per-subject statistics
    classes = Class.query.join(Enrollment).filter(
        Enrollment.student_id == profile.id,
        Enrollment.is_active == True
    ).all()
    
    