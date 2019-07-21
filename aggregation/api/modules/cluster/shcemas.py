from flask_marshmallow.fields import fields
from marshmallow import pre_load

from aggregation.api.modules.cluster import models
from aggregation import ma
from aggregation.common.functions import get_choices_value


class ClusterDetailSchema(ma.ModelSchema):
    class Meta:
        model = models.Cluster
        exclude = "cockroachdb_ca",


class ClusterSyncSchema(ma.ModelSchema):
    class Meta:
        model = models.Cluster

    @pre_load(pass_many=False)
    def pre_load(self, data, many=False):
        model = models.Cluster
        data['type'] = get_choices_value(data["type"], model.__type_choices__)
        data['status'] = get_choices_value(data["status"], model.__status_choices__)
        return data


class ClusterInspectInfoSyncSchema(ma.ModelSchema):
    class Meta:
        model = models.ClusterInspectInfo

    @pre_load
    def pre_load(self, data, many=False):
        data['node_num'] = data['nod_num']
        return {key: float(str(value).strip("%")) for key, value in data.items()}


class ClusterSchema(ma.ModelSchema):
    class Meta:
        model = models.Cluster


class ClusterInspectInfoDumpSchema(ma.ModelSchema):
    cluster = fields.Nested(ClusterSchema, many=False)

    class Meta:
        model = models.ClusterInspectInfo
