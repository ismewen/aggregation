from aggregation import ma
from aggregation.api.modules.tests.models import Parent, Child


class ParentModelSchema(ma.ModelSchema):
    class Meta:
        model = Parent


class SonModelSchema(ma.ModelSchema):
    class Meta:
        model = Child
