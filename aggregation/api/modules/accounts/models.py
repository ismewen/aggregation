import time

from flask import jsonify
from flask_login import UserMixin, login_user
from sqlalchemy.orm import object_session

from aggregation.extensions.bcrypt import bcrypt

from aggregation import db, exceptions


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(64), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    @classmethod
    def generate_password(cls, password):
        return bcrypt.generate_password_hash(password=password)

    @classmethod
    def find_by_password(cls, email, password, *args, **kwargs):
        email = email.strip()
        password = password.strip()

        if email and password:
            user = cls.query.filter(
                cls.email == email
            ).first()
            if user:
                pw_hash = bcrypt.generate_password_hash(password)
                if pw_hash == user.password:
                    return user

    def validate_password(self, password):
        pw_hash = bcrypt.generate_password_hash(password)
        return pw_hash == self.password

    @classmethod
    def login(cls, username, password, *args, **kwargs):

        user = cls.find_by_password(username=username, password=password)

        if not user:
            raise exceptions.InvalidEmailOrPassword()

        login_user(user)
        user.last_login_time = time.time()
        object_session(user).commit()

        return jsonify({"code": 1000, "message": 'success'})
