import datetime

from sqlalchemy import event
from sqlalchemy_utils import UUIDType
from flask_babel import gettext as _

from aggregation import db


class TransactionEnabled(object):
    """
    记录所有更改操作
    """
    pass


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(UUIDType(), primary_key=True)
    object_uuid = db.Column(UUIDType(), nullable=False, )
    object_id = db.Column(db.Integer)
    object_table = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    utime = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class TransactionRecord(db.Model):
    __tablename__ = "transaction_record"
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(UUIDType(), db.ForeignKey("transaction.id"))
    field = db.Column(db.String(32), doc=_("Field"))
    before = db.Column(db.PickleType, doc=_('Original Value'))
    after = db.Column(db.PickleType, doc=_('New Value'))
    transactions = db.relationship(Transaction, )


@event.listens_for(TransactionEnabled,  "mapper_configured", propagate=True)
def setup_listener(mapper, class_):

    obj_table = class_.__tablename__
    if isinstance(class_.id.type, UUIDType):
        remote = Transaction.object_uuid
    else:
        remote = Transaction.object_id
    class_.transactions = db.relation(
        Transaction,
        primaryjoin=db.and_(
            class_.id == db.foreign(db.remote(remote)),
            Transaction.object_table == obj_table
        ),
        cascade="all,delete",
        lazy='dynamic',
        backref=db.backref(obj_table)
    )

