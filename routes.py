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
    
   