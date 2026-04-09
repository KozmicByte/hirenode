from flask import Flask,render_template,request,redirect,url_for,flash
from model import db,User,StudentProfile,CompanyProfile,PlacementDrive,Application

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placement.db'
app.config['SECRET_KEY']='mysecret'
db.init_app(app)

# start db and create admin if not present
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin=User(username='admin',password='123',role='admin')
        db.session.add(admin)
        db.session.commit()


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
            if user.role=='admin':
                return redirect(url_for('admin_dashboard'))

            elif user.role=='company':
                if user.company_profile.status!='Approved':
                    return "Pending Admin Approval"
                return redirect(url_for('company_dashboard'))

            else:
                return redirect(url_for('student_dashboard'))

        else:
            return "Invalid Credentials"

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

    ongoing_drives=[]
    student_apps=[]

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


if __name__=='__main__':
    app.run(debug=True)