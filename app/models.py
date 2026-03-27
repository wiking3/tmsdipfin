from app import db
import bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', 'student'
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return password == self.password_hash

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    students = db.relationship('Student', backref='group', lazy="dynamic")
    homeworks = db.relationship('Homework', backref='group', lazy="dynamic")
    attendances = db.relationship('Attendance', backref='group', lazy="dynamic")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    homeworks = db.relationship('StudentHomework', backref='student', lazy="dynamic")

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    present = db.Column(db.Boolean, default=False)

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    student_homeworks = db.relationship('StudentHomework', backref='homework', lazy="dynamic")

class StudentHomework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    github_url = db.Column(db.String(256))
    submitted_date = db.Column(db.DateTime)
