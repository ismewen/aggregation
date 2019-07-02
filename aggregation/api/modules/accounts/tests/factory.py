import factory
from factory.alchemy import SQLAlchemyModelFactory

from aggregation import db
from aggregation.api.modules.accounts.models import User
from aggregation.extensions.bcrypt import bcrypt


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    username = factory.Faker('name')
    password = bcrypt.generate_password_hash("admin")

