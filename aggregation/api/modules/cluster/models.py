from sqlalchemy.ext.hybrid import hybrid_property

from aggregation import db
from sqlalchemy_utils import Timestamp


class Cluster(db.Model, Timestamp):
    __tablename__ = "cluster"
    __status_choices__ = (
        (100, "Active"),
        (200, "Inactive"),
        (300, "Full")

    )
    __type_choices__ = (
        (100, "CloudClusters Kubernetes"),
        (200, ""),
    )

    id = db.Column(db.Integer, primary_key=True, doc='Cluster Id')
    name = db.Column(db.String(128), doc='Cluster Name')
    type = db.Column(db.SmallInteger, default=100, doc='Cluster Type')
    region = db.Column(db.String(64), nullable=True, doc='Cluster Region')
    status = db.Column(db.SmallInteger, default=100, doc='Cluster Status')
    async_task_api_host = db.Column(db.String(64), doc='')
    storage_path_prefix = db.Column(db.String(32), doc='')
    cockroachdb_ca = db.Column(db.String(2048), doc='')

    def get_host(self):
        return self.async_task_api_host

    @hybrid_property
    def is_active(self):
        return self.status == 100


class ClusterInspectInfo(db.Model, Timestamp):
    __tablename__ = "cluster_inspect_info"
    id = db.Column(db.Integer, primary_key=True, doc='Cluster Inspect Info Id')
    pod_num = db.Column(db.Integer, doc="Pods Number")
    node_num = db.Column(db.Integer, doc='Nodes Number')
    cpu_lim_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Limit')
    cpu_req_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Request')
    cpu_usage_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Usage')
    mem_lim_avg = db.Column(db.Numeric(12, 6), doc="Average Memory Limit")
    mem_usage_avg = db.Column(db.Numeric(12, 6), doc="Average Memory Usage")

    @property
    def query_dict(self):
        columns = ClusterInspectInfo.__mapper__.columns
        return {column.name: getattr(self, column.name) for column in columns}


class ClusterDeployStrategy(db.Model, Timestamp):
    __tablename__ = "cluster_deploy_strategy"
    id = db.Column(db.Integer, primary_key=True, doc='Cluster Deploy Strategy Id')
    name = db.Column(db.String(32), doc="Strategy Name")
    status = db.Column(db.Integer, doc="Strategy Status")
    infix = db.Column(db.String(255), doc=u"Strategy infix")

