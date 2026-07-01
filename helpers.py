"""
AttendanceAI - Utility Helpers
"""
import os
import io
import csv
import json
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app, abort
from flask_login import current_user
from flask_mail import Message

logger = logging.getLogger(__name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from flask import redirect, url_for
                return redirect(url_for('auth.login'))
            if current_user.role.value not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_reset_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(hours=1)


def send_verification_email(mail, user, token: str):
    from flask import url_for, render_template
    try:
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        msg = Message(subject='Verify Your Email - AttendanceAI', recipients=[user.email],
                      html=render_template('email/verify_email.html', user=user, verify_url=verify_url))
        mail.send(msg)
        logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")


