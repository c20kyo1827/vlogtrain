from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

db = SQLAlchemy()
migrate = Migrate(compare_type=True)

class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    total_solve_problems = db.Column(db.Integer, server_default=text("0"), nullable=False)

class Catagory(db.Model):
    __tablename__ = "catagory"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id', ondelete='CASCADE'), nullable=False)

class Problem(db.Model):
    __tablename__ = "problem"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)