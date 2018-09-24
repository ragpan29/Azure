from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from app import login



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)


class User(TimestampMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin_rights = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.admin_rights == 1



class Employee(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(31))
    lname = db.Column(db.String(31))
    photo_url = db.Column(db.String(2083))
    department = db.Column(db.String(31))

    def to_dict(self):
        d = {
            "id":self.id,
            "fname": self.fname,
            "lname": self.lname,
            "photo_url": self.photo_url,
            "department": self.department
        }
        return d
