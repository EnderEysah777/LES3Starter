import os, csv
from flask import Flask, redirect, render_template, jsonify, request, send_from_directory, flash, url_for
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, IntegrityError
from App.models import db, User, Student, Course, StudentCourse
from datetime import timedelta

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)


def create_app():
  app = Flask(__name__, static_url_path='/static')
  CORS(app)
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

  app.app_context().push()
  return app


app = create_app()
db.init_app(app)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
  return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
  flash("Your session has expired. Please log in again.")
  return redirect(url_for('login'))


def parse_students():
  with open('students.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
      student = Student(id=row['ID'],
                        first_name=row['FirstName'],
                        image=row['Picture'],
                        last_name=row['LastName'],
                        programme=row['Programme'],
                        start_year=row['YearStarted'])
      db.session.add(student)
    db.session.commit()

def create_users():
  rob = User(username="rob", password="robpass")
  bob = User(username="bob", password="bobpass")
  sally = User(username="sally", password="sallypass")
  pam = User(username="pam", password="pampass")
  chris = User(username="chris", password="chrispass")
  db.session.add_all([rob, bob])
  db.session.commit()


def create_courses():
  info1601 = Course(code="INFO1601", name="Intro To WWW Programming")
  info2602 = Course(code="INFO2602", name="Web Programming & Technologies 1")
  info1600 = Course(code="INFO1600", name="IT Concepts")
  comp2605 = Course(code="COMP2605", name="Database Management Systems")
  db.session.add_all([info1601, info2602, info1600, comp2605])
  db.session.commit()


def initialize_db():
  db.drop_all()
  db.create_all()
  create_users()
  create_courses()
  parse_students()
  print('database intialized')


@app.route('/')
def login():
  return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_action():
  username = request.form.get('username')
  password = request.form.get('password')
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    response = redirect(url_for('home'))
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response
  else:
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/app')
@app.route('/app/<code>')
@jwt_required()
def home(code="INFO1601"):
  students = Student.query.all()
  courses = Course.query.all()
  selected_course = Course.query.filter_by(code=code).first()

  students_in_course = selected_course.students
  
  
  
  return render_template('index.html', user=current_user, students=students, courses=courses, selected_course=selected_course, courseStudents = students_in_course)

@app.route('/app/add_student', methods=['POST'])
@jwt_required()
def add_student():
  data = request.form
  student_course = StudentCourse(student_id=data['student_id'], course_id=data['course_id'])
  db.session.add(student_course)
  db.session.commit()

  return redirect(request.referrer)

@app.route('/app/delete_student/<id>')
@jwt_required()
def delete(id):
  student_course = StudentCourse.query.filter_by(student_id=id).first()
  db.session.delete(student_course)
  db.session.commit()
  return redirect(request.referrer)

@app.route('/logout')
def logout():
  response = redirect(url_for('login'))
  unset_jwt_cookies(response)
  flash('logged out')
  return response


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
