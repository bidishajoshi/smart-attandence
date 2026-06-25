"""
AttendanceAI — Application Entry Point
Run this file to start the development server.
"""
import os
from app import create_app, db
from app.models import (User, Student, Teacher, Department, Class,
                         Enrollment, FaceEmbedding, AttendanceSession,
                         AttendanceRecord, Notification, AuditLog, UserRole)

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Expose models in flask shell for easy debugging."""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Teacher': Teacher,
        'Department': Department,
        'Class': Class,
        'Enrollment': Enrollment,
        'FaceEmbedding': FaceEmbedding,
        'AttendanceSession': AttendanceSession,
        'AttendanceRecord': AttendanceRecord,
        'Notification': Notification,
        'AuditLog': AuditLog,
        'UserRole': UserRole,
    }


@app.cli.command('create-admin')
def create_admin():
    """CLI command to create a super admin user."""
    from app import bcrypt
    
    email = input('Admin email: ')
    password = input('Admin password: ')
    first_name = input('First name: ')
    last_name = input('Last name: ')
    
    if User.query.filter_by(email=email.lower()).first():
        print('❌ Email already registered.')
        return
    
    user = User(
        email=email.lower(),
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        role=UserRole.SUPER_ADMIN,
        first_name=first_name,
        last_name=last_name,
        is_verified=True,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    print(f'✅ Super Admin created: {user.full_name} ({user.email})')


@app.cli.command('seed-db')
def seed_db():
    """CLI command to seed the database with sample data."""
    from app import bcrypt
    from datetime import date
    
    print('🌱 Seeding database...')
    
    # Departments
    depts = [
        ('Computer Science', 'CS', 'Department of Computer Science and Engineering'),
        ('Electronics', 'EC', 'Department of Electronics and Communication'),
        ('Mechanical', 'ME', 'Department of Mechanical Engineering'),
        ('Civil', 'CE', 'Department of Civil Engineering'),
    ]
    
    dept_objs = []
    for name, code, desc in depts:
        existing = Department.query.filter_by(code=code).first()
        if not existing:
            dept = Department(name=name, code=code, description=desc)
            db.session.add(dept)
            dept_objs.append(dept)
        else:
            dept_objs.append(existing)
    db.session.flush()
    print(f'  ✓ Created {len(depts)} departments')
    
    # Admin
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
            role=UserRole.SUPER_ADMIN,
            first_name='System',
            last_name='Admin',
            is_verified=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.flush()
        print('  ✓ Created admin: admin@example.com / Admin@123')
    
    # Teacher
    if not User.query.filter_by(email='teacher@example.com').first():
        t_user = User(
            email='teacher@example.com',
            password_hash=bcrypt.generate_password_hash('Teacher@123').decode('utf-8'),
            role=UserRole.TEACHER,
            first_name='Dr. Priya',
            last_name='Sharma',
            is_verified=True,
            is_active=True
        )
        db.session.add(t_user)
        db.session.flush()
        teacher = Teacher(
            user_id=t_user.id,
            employee_id='FAC001',
            department_id=dept_objs[0].id,
            designation='Assistant Professor',
            is_approved=True
        )
        db.session.add(teacher)
        db.session.flush()
        print('  ✓ Created teacher: teacher@example.com / Teacher@123')
    
    # Student
    if not User.query.filter_by(email='student@example.com').first():
        s_user = User(
            email='student@example.com',
            password_hash=bcrypt.generate_password_hash('Student@123').decode('utf-8'),
            role=UserRole.STUDENT,
            first_name='Rahul',
            last_name='Kumar',
            is_verified=True,
            is_active=True
        )
        db.session.add(s_user)
        db.session.flush()
        student = Student(
            user_id=s_user.id,
            roll_number='CS2024001',
            department_id=dept_objs[0].id,
            semester=3,
            batch_year=2024,
            section='A',
            is_approved=True,
            face_registered=False
        )
        db.session.add(student)
        print('  ✓ Created student: student@example.com / Student@123')
    
    db.session.commit()
    print('\n✅ Database seeded successfully!')
    print('\nTest Credentials:')
    print('  Admin:   admin@example.com   / Admin@123')
    print('  Teacher: teacher@example.com / Teacher@123')
    print('  Student: student@example.com / Student@123')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)