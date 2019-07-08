from flask import Blueprint

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

    allow_actions = []

    detail_schema = shcemas.ClusterSyncSchema

    @action(detail=False)
    @url_params_require(mandatory_params=['region', 'product_name'])
    def most_suitable_deploy_cluster(self):
        region = mandatory_params.get('region')
        product_name = mandatory_params.get('product_name')
        return "product name, region"


ClusterAPIView.register_to(blueprint_or_app=blueprint)
