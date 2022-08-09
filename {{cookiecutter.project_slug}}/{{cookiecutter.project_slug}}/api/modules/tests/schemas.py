from {{cookiecutter.project_slug}} import ma
from {{cookiecutter.project_slug}}.api.modules.tests.models import Parent, Child


class ParentModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parent


class SonModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Child

