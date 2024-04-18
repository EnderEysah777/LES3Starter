from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  def __init__(self, username, password):
    self.username= username
    self.set_password(password)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)
    
class Student(db.Model):
  id = db.Column(db.String(9), primary_key=True)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(80), nullable=False)
  programme = db.Column(db.String(80), nullable=False)
  start_year = db.Column(db.Integer, nullable=False)
  image = db.Column(db.String(80), nullable=False)
  # courses = db.relationship('StudentCourse', secondary='student_course', backref='students')
  courses = db.relationship('Course', secondary='student_course', backref='students')

  def __init__(self, id, first_name, last_name, programme, start_year, image):
    self.id = id
    self.first_name = first_name
    self.last_name = last_name
    self.programme = programme
    self.start_year = start_year
    self.image = image


  
class Course(db.Model):
  code = db.Column(db.String(9), primary_key=True)
  name = db.Column(db.String(80), nullable=False)

  def __init__(self, code, name):
    self.code = code
    self.name = name
  


class StudentCourse(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  student_id= db.Column(db.String(9), db.ForeignKey('student.id'), nullable=False)
  course_id = db.Column(db.String(9), db.ForeignKey('course.code'), nullable=False)
  

  def __init__(self, student_id, course_id):
    self.student_id = student_id
    self.course_id = course_id


