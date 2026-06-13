
"""
AttendanceAI - Smart Attendance System
Configuration Module
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
 
load_dotenv()
 
class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    
Claude finished the response

PROJECT: Smart Attendance System Using Face Recognition (Production Ready) Build a complete enterprise-grade Smart Attendance System using Python, Flask, PostgreSQL, OpenCV, Face Recognition, HTML, CSS, JavaScript, Bootstrap/Tailwind. GOAL: Create a fully functional, professional, launch-read

pasted

Jun 12

Check available skills
Check available skills
This is a massive enterprise project. Let me build a comprehensive, production-ready Smart Attendance System. I'll create the complete codebase with all modules.


Created 23 files, ran a command
Created 23 files, ran a command

Create project structure

Script

Main requirements file
requirements.txt

Environment configuration
.env.example

Main Flask app configuration
config.py

Flask app factory
__init__.py

Database models
__init__.py

Face recognition utility module
face_recognition_util.py

Utility helpers module
helpers.py

Utils init
__init__.py

Auth forms
forms.py

Auth blueprint routes
routes.py

Auth blueprint init
__init__.py

Main blueprint (landing + dashboard redirect)
__init__.py

Main routes
routes.py

Admin blueprint init and routes
__init__.py

Admin routes
routes.py

Student blueprint
__init__.py

Student routes
routes.py

Teacher blueprint init
__init__.py

Teacher routes
routes.py

Attendance and analytics blueprints
__init__.py

Attendance routes
routes.py

Analytics blueprint
__init__.py

Analytics routes
routes.py
Done
Now let me build all the HTML templates — the most crucial part for the premium UI:


Base HTML template with premium design system
Base HTML template with premium design system
continue

Jun 12

Architected comprehensive dashboard template showcasing integrated features
Architected comprehensive dashboard template showcasing integrated features
continue

1:22 PM

Created 7 files
Created 7 files


You are out of free messages until 6:15 PM
Claude Fable 5 is currently unavailable.
Learn more(opens in new tab)




Claude is AI and can make mistakes. Please double-check responses.
Config · PY
"""
AttendanceAI - Smart Attendance System
Configuration Module
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
 
load_dotenv()
 
class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/attendance_db'
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@attendanceai.com')
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Face Recognition
    FACE_RECOGNITION_TOLERANCE = float(os.environ.get('FACE_RECOGNITION_TOLERANCE', 0.5))
    MAX_FACE_IMAGES = int(os.environ.get('MAX_FACE_IMAGES', 10))
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
 
 
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False
 
 
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
 
 
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
 
 
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
 
