import factory
from factory.alchemy import SQLAlchemyModelFactory

from {{cookiecutter.project_slug}}.api.modules.tests.models import Parent, Child
from {{cookiecutter.project_slug}} import db


class ParentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parent
        sqlalchemy_session = db.session

    name = factory.Faker('name')


class ChildFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Child
        sqlalchemy_session = db.session

    name = factory.Faker('name')
    parent = factory.SubFactory(ParentFactory)


