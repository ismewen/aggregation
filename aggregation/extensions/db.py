from flask_sqlalchemy import SQLAlchemy, Model, BaseQuery, DefaultMeta, _QueryProperty
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy_utils import render_statement
registry = {}


class CustomQuery(BaseQuery):

    def print_query(self, bind=None):
        return render_statement(self, bind=bind)


class CustomSQLAlchemy(SQLAlchemy):

    def __init__(self, *args, **kwargs):
        self.class_registry = {}
        super(CustomSQLAlchemy, self).__init__(*args, **kwargs)

    def make_declarative_base(self, model, metadata=None, track_registry=True):
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=DefaultMeta,
                class_registry=self.class_registry if track_registry else None
            )

        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    def get_model(self, model_name):
        return self.class_registry.get(model_name)


db = CustomSQLAlchemy(query_class=CustomQuery)
