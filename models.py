from db import db
from sqlalchemy.dialects.postgresql import JSONB

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.Text, primary_key=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)

class Block(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Text, unique=True, nullable=False)
    previous_hash = db.Column(db.Text, nullable=False)
    nonce = db.Column(db.BigInteger, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default="NOW()")

    transactions = db.relationship("Transaction", backref="block", lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id', ondelete='CASCADE'))
    data = db.Column(JSONB, nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)

class ClassModel(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Text, unique=True, nullable=False)
    course = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.Text, nullable=False)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Text, db.ForeignKey('classes.class_id'))
    student_id = db.Column(db.Text, db.ForeignKey('students.student_id'))
    status = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
