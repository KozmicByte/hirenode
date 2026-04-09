from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, StudentProfile, CompanyProfile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SECRET_KEY'] = 'mysecret' # Required for flashing messages
db.init_app(app)

# Create DB and Admin on start
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', password='123', role='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)