import copy
import unittest
from flask import url_for

from aggregation import db
from aggregation.api.modules.cluster.models import Cluster, ClusterInspectInfo, create_default_deploy_strategy, \
    ClusterDeployStrategy
from aggregation.api.modules.cluster.strategy import StrategyUtil
from aggregation.api.modules.cluster.tests.factorys import ClusterFactory
from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase
from aggregation.remote_apps.agent_server.bases import AgentServerClient

from aggregation.api.modules.cluster.tasks import ClusterInfoSync, ClusterInspectInfoRecordSync, \
    cluster_info_record_sync


class ClusterTestCase(AggregationAuthorizedTestCase):

    @unittest.skip
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

    def test_get_available_cluster(self):
        uri = url_for("clusters.ClusterAPIView-get-available-deploy-cluster")
        res = self.client.get(uri)
        self.assert400(res)
        self.assertTrue(res.json.get("code") == 1006)
        self.test_cluster_info_sync()
        uri = url_for("clusters.ClusterAPIView-get-available-deploy-cluster")
        res = self.client.get(uri)
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
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client_cls=AgentServerClient)
        info = sync.get_cluster_inspect_info()
        self.assertEqual('return_code' in info, True)
        print(info)

    def test_save_cluster_inspect_info(self):
        self.test_cluster_info_sync()
        cluster = Cluster.query.filter(Cluster.can_ask_inspect_info).filter(Cluster.is_active).first()
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client_cls=AgentServerClient)
        obj = sync.save_record()
        self.assertTrue(isinstance(obj, ClusterInspectInfo))

    def test_sync_cluster_info_record_task(self):
        self.test_cluster_info_sync()
        cluster_info_record_sync()
        count = ClusterInspectInfo.query.count()
        self.assertTrue(count > 0)

    def test_sentry(self):
        a = 1 / 0
        self.assertRaises(AttributeError, a)

class ClusterStrategyTestCase(AggregationAuthorizedTestCase):

    def test_success_strategy(self):
        inspect_info = self.create_strategy_success_info()
        su = StrategyUtil(inspect_info)
        strategy = su.get_strategy()
        self.assertTrue(isinstance(strategy, ClusterDeployStrategy))

        flag = su.is_strategy_success(strategy=strategy)

        strategy_str = strategy.get_format_str()
        cluster_info = su.dump_cluster_inspect_info()

        content = strategy_str + "\n" + cluster_info

        print(content)
        self.assertTrue(flag)

    @classmethod
    def create_strategy_success_info(cls):
        from aggregation.api.modules.cluster.shcemas import ClusterInspectInfoSyncSchema
        cluster = ClusterFactory()
        data = {
            'cpu_lim_avg': 245,
            'cpu_req_avg': 18,
            'cpu_usage_avg': 8.33333,
            'mem_lim_avg': 112,
            'mem_req_avg': 4,
            'mem_usage_avg': 25.6667,
            'nod_num': 3,
            'pod_num': 95,
        }
        s = ClusterInspectInfoSyncSchema()
        inspect_info, error = s.load(data)
        inspect_info.cluster = cluster
        create_default_deploy_strategy()

        db.session.add(inspect_info)
        db.session.commit()
        return inspect_info

    @classmethod
    def create_strategy_failed_info(cls):
        from aggregation.api.modules.cluster.shcemas import ClusterInspectInfoSyncSchema
        cluster = ClusterFactory()
        data = {
            'cpu_lim_avg': 245,
            'cpu_req_avg': 18,
            'cpu_usage_avg': 8.33333,
            'mem_lim_avg': 112,
            'mem_req_avg': 4,
            'mem_usage_avg': 85.6667,
            'nod_num': 3,
            'pod_num': 95,
        }
        s = ClusterInspectInfoSyncSchema()
        inspect_info, error = s.load(data)
        inspect_info.cluster = cluster
        create_default_deploy_strategy()

        db.session.add(inspect_info)
        db.session.commit()
        return inspect_info

    def test_failed_strategy(self):
        inspect_info = self.create_strategy_failed_info()
        su = StrategyUtil(inspect_info)
        strategy = su.get_strategy()
        self.assertTrue(isinstance(strategy, ClusterDeployStrategy))

        flag = su.is_strategy_success(strategy=strategy)

        strategy_str = strategy.get_format_str()
        cluster_info = su.dump_cluster_inspect_info()

        content = strategy_str + "\n" + cluster_info

        print(content)
        self.assertFalse(flag)

    def test_apply_success_strategy(self):
        inspect_info = self.create_strategy_success_info()
        su = StrategyUtil(inspect_info)
        su.cluster.make_full()
        su.apply_strategy()
        self.assertTrue(su.cluster.is_active)

    def test_apply_failed_strategy(self):
        inspect_info = self.create_strategy_failed_info()
        su = StrategyUtil(inspect_info)
        self.assertFalse(su.cluster.is_full)
        su.apply_strategy()
        self.assertTrue(su.cluster.is_full)
