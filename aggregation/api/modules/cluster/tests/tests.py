import copy

from flask import url_for

from aggregation.api.modules.cluster.models import Cluster, ClusterInspectInfo
from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase
from aggregation.remote_apps.agent_server.bases import AgentServerClient

from aggregation.api.modules.cluster.tasks import ClusterInfoSync, ClusterInspectInfoRecordSync, \
    cluster_info_record_sync


class ClusterTestCase(AggregationAuthorizedTestCase):

    def test_mandatory_query_params(self):
        uri = url_for("clusters.ClusterAPIView-most-suitable-deploy-cluster")
        res = self.client.get(uri)
        self.assert400(response=res)
        data = {
            "region": "Europe",
            "product_name": "mongodb",
        }
        res = self.client.get(uri, params=data)
        self.assert200(res)

    def test_cluster_info_sync(self):
        cluster_sync = ClusterInfoSync()
        clusters_data = cluster_sync.requests_cluster_info()
        clusters_backup = copy.deepcopy(clusters_data)
        cluster_sync.upserts(clusters_info=clusters_data)
        cluster = Cluster.query.filter(Cluster.id == 1).first()
        self.assertEqual(isinstance(cluster, Cluster), True)
        pre_name = cluster.name
        for x in clusters_backup:
            if x.get("id") == 1:
                x['name'] = "wenjun"
        cluster_sync.upserts(clusters_backup)
        cluster = Cluster.query.filter(Cluster.id == 1).first()
        self.assertNotEqual(pre_name, cluster.name)
        self.assertEqual(cluster.name, "wenjun")

    def test_get_cluster_inspect_info(self):
        self.test_cluster_info_sync()
        cluster = Cluster.query.filter(Cluster.is_active).first()
        client = AgentServerClient(cluster)
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client=client)
        info = sync.get_cluster_inspect_info()
        self.assertEqual('return_code' in info, True)
        print(info)

    def test_save_cluster_inspect_info(self):
        self.test_cluster_info_sync()
        cluster = Cluster.query.filter(Cluster.is_active).first()
        client = AgentServerClient(cluster)
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client=client)
        obj = sync.save_record()
        self.assertTrue(isinstance(obj, ClusterInspectInfo))

    def test_sync_cluster_info_task(self):
        self.test_cluster_info_sync()
        cluster_info_record_sync()
        count = ClusterInspectInfo.query.count()
        self.assertTrue(count > 0)
