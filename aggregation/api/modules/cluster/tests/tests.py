import copy

from flask import url_for

from aggregation.api.modules.cluster.models import Cluster, ClusterInspectInfo, create_default_deploy_strategy, ClusterDeployStrategy
from aggregation.api.modules.cluster.strategy import StrategyUtil
from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase
from aggregation.remote_apps.agent_server.bases import AgentServerClient

from aggregation.api.modules.cluster.tasks import ClusterInfoSync, ClusterInspectInfoRecordSync, \
    cluster_info_record_sync


class ClusterTestCase(AggregationAuthorizedTestCase):

    def test_mandatory_query_params(self):
        uri = url_for("clusters.ClusterAPIView-get-available-deploy-cluster")
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
        cluster = Cluster.query.filter(Cluster.can_ask_inspect_info).filter(
            Cluster.is_active
        ).first()
        client = AgentServerClient(cluster)
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client=client)
        info = sync.get_cluster_inspect_info()
        self.assertEqual('return_code' in info, True)
        print(info)

    def test_save_cluster_inspect_info(self):
        self.test_cluster_info_sync()
        cluster = Cluster.query.filter(Cluster.can_ask_inspect_info).filter(Cluster.is_active).first()
        client = AgentServerClient(cluster)
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client=client)
        obj = sync.save_record()
        self.assertTrue(isinstance(obj, ClusterInspectInfo))

    def test_sync_cluster_info_record_task(self):
        self.test_cluster_info_sync()
        cluster_info_record_sync()
        count = ClusterInspectInfo.query.count()
        self.assertTrue(count > 0)


class ClusterStrategyTestCase(AggregationAuthorizedTestCase):

    def test_get_strategy(self):
        m = ClusterTestCase()
        m.test_sync_cluster_info_record_task()
        create_default_deploy_strategy()
        lasted_inspect_info = ClusterInspectInfo.query.first()
        su = StrategyUtil(lasted_inspect_info)
        strategy = su.get_strategy()
        self.assertTrue(isinstance(strategy, ClusterDeployStrategy))
        # todo is expression 测试
        su.is_expression_success()
        su.is_strategy_success()



