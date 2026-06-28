"""
AttendanceAI - Authentication Forms
"""
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SelectField,
                     IntegerField, DateField, TextAreaField, EmailField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                 ValidationError, Optional, NumberRange)
from app.models import User


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class StudentRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(3, 20)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', coerce=int,
                            choices=[(i, f'Semester {i}') for i in range(1, 9)],
                            validators=[DataRequired()])
    batch_year = IntegerField('Batch Year', validators=[DataRequired(), NumberRange(2000, 2099)])
    section = StringField('Section', validators=[Optional(), Length(1, 5)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(8, 128, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_roll_number(self, field):
        from app.models import Student
        if Student.query.filter_by(roll_number=field.data.upper()).first():
            raise ValidationError('Roll number already registered.')


class TeacherRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(3, 20)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    designation = StringField('Designation', validators=[Optional(), Length(2, 100)])
    qualification = StringField('Qualification', validators=[Optional(), Length(2, 200)])
    specialization = StringField('Specialization', validators=[Optional(), Length(2, 200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_employee_id(self, field):
        from app.models import Teacher
        if Teacher.query.filter_by(employee_id=field.data.upper()).first():
            raise ValidationError('Employee ID already registered.')


class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])


class ProfileUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])