import datetime
import os
import json

from typing import List

import arrow
from aggregation.api.modules.cluster.models import Cluster, ClusterInspectInfo
from aggregation.api.modules.cluster.shcemas import ClusterSyncSchema, ClusterInspectInfoSyncSchema
from aggregation.api.modules.cluster.strategy import StrategyUtil
from aggregation.remote_apps.agent_server.bases import AgentServerClient
from celery_app import celery

from aggregation import settings, db


def path_join(path, join_list) -> str:
    for name in join_list:
        path = os.path.join(path, name)
    return path


class ClusterInfoSync(object):
    file_name = "cluster.json"

    @classmethod
    def requests_cluster_info(cls) -> List:
        path = path_join(settings.APP_ROOT, ["aggregation", "api", "modules", "cluster", "data", 'cluster.json'])
        with open(path) as f:
            clusters_info = json.load(f)
        return clusters_info

    def upserts(self, clusters_info: List) -> None:
        s = ClusterSyncSchema()
        for cluster_info in clusters_info:
            instance = Cluster.query.filter(Cluster.id == cluster_info.get("id")).first()
            obj, error = s.load(instance=instance, data=cluster_info, session=db.session)
            if not error:
                db.session.add(obj)
        db.session.commit()

    def sync(self):
        info = self.requests_cluster_info()
        self.upserts(clusters_info=info)


class ClusterInspectInfoRecordSync(object):

    def __init__(self, cluster: Cluster, client_cls: type(AgentServerClient)):
        self.cluster = cluster
        self.client = client_cls(cluster)

    def get_cluster_inspect_info(self):
        res = self.client.api_cluster.get_cluster_info()
        return res.json()

    def save_record(self):
        s = ClusterInspectInfoSyncSchema()
        info = self.get_cluster_inspect_info()
        obj, error = s.load(info)
        obj.cluster = self.cluster
        if not error:
            db.session.add(obj)
        return obj


@celery.task()
def cluster_info_record_sync():
    clusters = Cluster.query.filter(Cluster.can_ask_inspect_info).filter(
        Cluster.is_active
    ).all()
    for cluster in clusters:
        client = AgentServerClient(cluster)
        sync = ClusterInspectInfoRecordSync(cluster=cluster, client=client)
        sync.save_record()
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    finally:
        cluster_status_strategy.delay()


@celery.task()
def cluster_status_strategy():
    clusters = Cluster.query.filter(Cluster.can_ask_inspect_info).all()
    for cluster in clusters:
        latest_inspect_info = ClusterInspectInfo.query.filter(
            ClusterInspectInfo.cluster == cluster
        ).filter(
            # seven seven seven
            ClusterInspectInfo.created > arrow.now() - datetime.timedelta(minutes=7)
        ).order_by(
            ClusterInspectInfo.id.desc()
        ).first()
        if not latest_inspect_info:
            continue
        su = StrategyUtil(latest_inspect_info)
        su.apply_strategy()
