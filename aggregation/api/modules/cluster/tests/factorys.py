import random

import factory
from factory.alchemy import SQLAlchemyModelFactory

from aggregation import db
from aggregation.api.modules.cluster.models import Cluster, ClusterInspectInfo


class ClusterFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Cluster
        sqlalchemy_session = db.session

    name = factory.Faker('name')


class ClusterInspectFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ClusterInspectInfo
        sqlalchemy_session = db.session

    pods_num = factory.Sequence(lambda n: random.randint(0, n*10))
    nods_num = factory.Sequence(lambda n: random.randint(0, n*10))
