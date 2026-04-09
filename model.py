from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True)  # For blacklisting
    
    # Relationships to profile details
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False)

class CompanyProfile(db.Model):
    __tablename__ = "company_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(50))
    website = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

class StudentProfile(db.Model):
    __tablename__ = "student_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(200)) # Stores the filename
    
    applications = db.relationship('Application', backref='student', lazy=True)

class PlacementDrive(db.Model):
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    salary_range = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending') # Pending, Approved, Closed
    
    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    # Status: Applied, Shortlisted, Selected, Rejected
    status = db.Column(db.String(20), default='Applied') 
    
    # Unique constraint to prevent duplicate applications for the same drive
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)