from werkzeug.utils import find_modules

from aggregation import db
from aggregation.api.modules.transactions.models import TransactionEnabled


class Parent(TransactionEnabled, db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=255))
    children = db.relationship("Child")


class Child(TransactionEnabled, db.Model):
    __tablename__ = 'child'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=255))
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    parent = db.relationship("Parent")
find_modules