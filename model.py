from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

#table to store users and thier roles
class User(db.Model):
    __tablename__='users'

    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(10),nullable=False)#role can be admin,comp,student
    is_active=db.Column(db.Boolean,default=True)#if admin has blscklisted
    #reverse the relations, svae the join queries
    student_profile=db.relationship('StudentProfile',backref='user',uselist=False)
    company_profile=db.relationship('CompanyProfile',backref='user',uselist=False)

#all info about the company
class CompanyProfile(db.Model):
    __tablename__='company_profiles'

    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    name=db.Column(db.String(100),nullable=False)
    hr_contact=db.Column(db.String(50))
    website=db.Column(db.String(100))
    industry=db.Column(db.String(50))
    status=db.Column(db.String(20),default='Pending')

    drives=db.relationship('PlacementDrive',backref='company',lazy=True)

#student profile
class StudentProfile(db.Model):
    __tablename__='student_profiles'

    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    full_name=db.Column(db.String(100),nullable=False)
    contact=db.Column(db.String(20))
    education=db.Column(db.Text)
    skills=db.Column(db.Text)
    resume_path=db.Column(db.String(200))

    applications=db.relationship('Application',backref='student',lazy=True)

#all info about the drive
class PlacementDrive(db.Model):
    __tablename__='placement_drives'

    id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('company_profiles.id'),nullable=False)
    job_title=db.Column(db.String(100),nullable=False)
    job_description=db.Column(db.Text,nullable=False)
    eligibility=db.Column(db.Text)
    deadline=db.Column(db.DateTime,nullable=False)
    salary_range=db.Column(db.String(50))
    status=db.Column(db.String(20),default='Pending')

    applications=db.relationship('Application',backref='drive',lazy=True)


class Application(db.Model):
    __tablename__='applications'

    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('student_profiles.id'),nullable=False)
    drive_id=db.Column(db.Integer,db.ForeignKey('placement_drives.id'),nullable=False)
    date_applied=db.Column(db.DateTime,default=datetime.now)
    status=db.Column(db.String(20),default='Applied')

    __table_args__=(
        db.UniqueConstraint('student_id','drive_id',name='_student_drive_uc'),
    )