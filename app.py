import os
from flask import Flask,render_template,request,redirect,url_for,flash
from model import db,User,StudentProfile,CompanyProfile,PlacementDrive,Application
from flask import send_from_directory
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement.db'
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin=User(username='admin',password='123',role='admin')
        db.session.add(admin)
        db.session.commit()

UPLOAD_FOLDER='static/resumes'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        uname=request.form.get('username')
        pwd=request.form.get('password')
        user=User.query.filter_by(username=uname,password=pwd).first()
        
        if user:
            if not user.is_active:
                return "Your account is deactivated."
            if user.role=='admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role=='company':
                if user.company_profile and user.company_profile.status=='Approved':
                    return redirect(url_for('company_dashboard',user_id=user.id))
                else:
                    return "Your company is either not registered or pending approval."
            elif user.role=='student':
                return redirect(url_for('student_dashboard',user_id=user.id))
        else:
            return "Invalid Username or Password"
    return render_template('login.html')

@app.route('/register/student',methods=['GET','POST'])
def register_student():
    if request.method=='POST':
        uname=request.form.get('username')
        pwd=request.form.get('password')
        fname=request.form.get('full_name')

        new_user=User(username=uname,password=pwd,role='student')
        db.session.add(new_user)
        db.session.commit()

        new_profile=StudentProfile(user_id=new_user.id,full_name=fname)
        db.session.add(new_profile)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register_student.html')

@app.route('/register/company',methods=['GET','POST'])
def register_company():
    if request.method=='POST':
        uname=request.form.get('username')
        pwd=request.form.get('password')
        cname=request.form.get('company_name')

        new_user=User(username=uname,password=pwd,role='company')
        db.session.add(new_user)
        db.session.commit()

        new_profile=CompanyProfile(user_id=new_user.id,name=cname,status='Pending')
        db.session.add(new_profile)
        db.session.commit()

        return "Registration successful! Wait for Admin approval."
    return render_template('register_company.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    search_query=request.args.get('search','')

    students_query=StudentProfile.query
    companies_query=CompanyProfile.query.filter_by(status='Approved')

    if search_query:
        students_query=students_query.filter(StudentProfile.full_name.contains(search_query))
        companies_query=companies_query.filter(CompanyProfile.name.contains(search_query))

    all_students=students_query.all()
    approved_companies=companies_query.all()
    pending_companies=CompanyProfile.query.filter_by(status='Pending').all()

    ongoing_drives=PlacementDrive.query.filter_by(status='Approved').all()
    student_apps=Application.query.all()

    return render_template('admin_dashboard.html',
        students=all_students,
        approved_comps=approved_companies,
        pending_comps=pending_companies,
        ongoing_drives=ongoing_drives,
        student_apps=student_apps,
        search_query=search_query)

@app.route('/admin/toggle_user/<int:user_id>')
def toggle_user(user_id):
    user=User.query.get(user_id)
    if user:
        user.is_active=not user.is_active
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_company/<int:comp_id>')
def approve_company(comp_id):
    comp=CompanyProfile.query.get(comp_id)
    if comp:
        comp.status='Approved'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/company/dashboard/<int:user_id>')
def company_dashboard(user_id):
    user=User.query.get(user_id)
    comp=user.company_profile
    active=PlacementDrive.query.filter_by(company_id=comp.id,status='Approved').all()
    closed=PlacementDrive.query.filter_by(company_id=comp.id,status='Closed').all()
    return render_template('company_dashboard.html',comp=comp,active=active,closed=closed,user_id=user_id)

@app.route('/company/create_drive/<int:user_id>',methods=['GET','POST'])
def create_drive(user_id):
    if request.method=='POST':
        user=User.query.get(user_id)
        new_drive=PlacementDrive(
            company_id=user.company_profile.id,
            job_title=request.form.get('job_title'),
            job_description=request.form.get('description'),
            eligibility=request.form.get('eligibility'),
            deadline=datetime.strptime(request.form.get('deadline'),'%Y-%m-%d'),
            status='Approved'
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company_dashboard',user_id=user_id))
    return render_template('create_drive.html',user_id=user_id)

@app.route('/company/view_applicants/<int:drive_id>/<int:user_id>')
def view_applicants(drive_id,user_id):
    drive=PlacementDrive.query.get(drive_id)
    return render_template('view_applicants.html',drive=drive,user_id=user_id)

@app.route('/company/update_status/<int:app_id>/<int:user_id>',methods=['POST'])
def update_status(app_id,user_id):
    application=Application.query.get(app_id)
    if application:
        application.status=request.form.get('new_status')
        db.session.commit()
    return redirect(url_for('view_applicants',drive_id=application.drive_id,user_id=user_id))

@app.route('/company/close_drive/<int:drive_id>/<int:user_id>')
def close_drive(drive_id,user_id):
    drive=PlacementDrive.query.get(drive_id)
    if drive:
        drive.status='Closed'
        db.session.commit()
    return redirect(url_for('company_dashboard',user_id=user_id))

@app.route('/student/dashboard/<int:user_id>')
def student_dashboard(user_id):
    user=User.query.get(user_id)
    student=user.student_profile
    
    all_drives=PlacementDrive.query.filter_by(status='Approved').all()
    my_applications=Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids=[app.drive_id for app in my_applications]
    
    return render_template('student_dashboard.html',
        student=student,
        drives=all_drives,
        my_apps=my_applications,
        applied_ids=applied_drive_ids,
        user_id=user_id)

@app.route('/student/apply/<int:drive_id>/<int:user_id>')
def apply_to_drive(drive_id,user_id):
    user=User.query.get(user_id)
    student=user.student_profile
    
    existing=Application.query.filter_by(student_id=student.id,drive_id=drive_id).first()
    
    if not existing:
        new_app=Application(student_id=student.id,drive_id=drive_id,status='Applied')
        db.session.add(new_app)
        db.session.commit()
    return redirect(url_for('student_dashboard',user_id=user_id))

@app.route('/student/profile/<int:user_id>',methods=['GET','POST'])
def edit_profile(user_id):
    user=User.query.get(user_id)
    student=user.student_profile
    
    if request.method=='POST':
        student.full_name=request.form.get('full_name')
        student.education=request.form.get('education')
        student.skills=request.form.get('skills')
        
        file=request.files.get('resume')
        if file and file.filename!='':
            filename=f"student_{student.id}_{file.filename}"
            file.save(os.path.join(UPLOAD_FOLDER,filename))
            student.resume_path=filename
            
        db.session.commit()
        return redirect(url_for('student_dashboard',user_id=user_id))
        
    return render_template('edit_profile.html',student=student,user_id=user_id)

@app.route('/drive/details/<int:drive_id>/<int:user_id>')
def drive_details(drive_id,user_id):
    drive=PlacementDrive.query.get(drive_id)
    return render_template('drive_details.html',drive=drive,user_id=user_id)

@app.route('/application/view/<int:app_id>/<int:user_id>')
def view_application(app_id,user_id):
    app_record=Application.query.get(app_id)
    return render_template('application_view.html',app=app_record,user_id=user_id)

@app.route('/view_resume/<filename>')
def view_resume(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

if __name__=='__main__':
    app.run(debug=True)