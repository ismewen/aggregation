import time

from bcrypt import hashpw, gensalt
from flask import jsonify
from flask_login import UserMixin, login_user
from sqlalchemy.orm import object_session

from aggregation.extensions.bcrypt import bcrypt

from aggregation import db, exceptions


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40), unique=True)
    password = db.Column(db.Binary(70))
    email = db.Column(db.String(64), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def set_password(self, password):
        self.password = hashpw(password.encode("utf-8"), gensalt())

    @classmethod
    def find_by_password(cls, email, password, *args, **kwargs):
        email = email.strip()
        password = password.strip()
        if email and password:
            user = cls.query.filter(
                cls.email == email
            ).first()
            if user and user.check_password(password):
                    return user

    def check_password(self, password):
        pw_hash = hashpw(password=password.encode("utf-8"), salt=self.password)
        return pw_hash == self.password

    @classmethod
    def login(cls, email, password, *args, **kwargs):

        user = cls.find_by_password(email=email, password=password)

        if not user:
            raise exceptions.InvalidEmailOrPassword()

        login_user(user)
        user.last_login_time = time.time()
        object_session(user).commit()

        return jsonify({"code": 1000, "message": 'success'})
