import random

from flask import Blueprint, request

from aggregation.api.modules.cluster import models
from aggregation.core.decorators import action, url_params_require
from aggregation.core.proxy import mandatory_params
from aggregation.core.views import APIView
from aggregation.api.modules.cluster import shcemas

blueprint = Blueprint('clusters',
                      __name__,
                      template_folder='templates',
                      url_prefix='/clusters')


class ClusterAPIView(APIView):
    name = 'cluster'
    path = '/clusters'

    model = models.Cluster

    allow_actions = []

    detail_schema = shcemas.ClusterDetailSchema

    @action(detail=False)
    def get_available_deploy_cluster(self, *args, **kwargs):
        region = request.args.get('region')
        query = self.get_query(*args, **kwargs)
        query = query.filter(models.Cluster.is_active)
        if region:
            query = query.filter(models.Cluster.region == region)
        limit = query.count() - 1
        limit = limit if limit > -1 else 0
        the_cluster = query[random.randint(0, limit)]
        s = self.detail_schema()
        return s.dump(the_cluster).data


ClusterAPIView.register_to(blueprint_or_app=blueprint)
