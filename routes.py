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


