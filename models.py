from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    operations = db.relationship('Operation', backref='employee', lazy=True)


class Operation(db.Model):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    validated = db.Column(db.Boolean, default=False)
    researcher_confirmed = db.Column(db.Boolean, default=False)  # New field
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    phytosanitary_id = db.Column(
        db.Integer, db.ForeignKey('phytosanitary.id'), nullable=True)


class Phytosanitary(db.Model):
    __tablename__ = 'phytosanitary'
    id = db.Column(db.Integer, primary_key=True)
    diseases_targeted = db.Column(db.String(200), nullable=False)
    disease_stage = db.Column(db.String(100), nullable=False)
    treatment_methods = db.Column(db.String(200), nullable=False)
    observations = db.Column(db.String(300), nullable=True)
    operations = db.relationship(
        'Operation', backref='phytosanitary', lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # e.g., "researcher" or "chief"
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
