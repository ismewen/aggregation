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
    def can_ask_inspect_info(self):
        return self.status in [100, 200]

    @can_ask_inspect_info.expression
    def can_ask_inspect_info(self):
        return self.status.in_([100, 200])

    @hybrid_property
    def is_active(self):
        return self.status == 100

    def make_full(self):
        self.status = 200

class ClusterInspectInfo(db.Model, Timestamp):
    __tablename__ = "cluster_inspect_info"
    id = db.Column(db.Integer, primary_key=True, doc='Cluster Inspect Info Id')
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'))
    cluster = db.relationship(Cluster, backref=db.backref('inspect_records'))
    pod_num = db.Column(db.Integer, doc="Pods Number")
    node_num = db.Column(db.Integer, doc='Nodes Number')
    cpu_lim_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Limit')
    cpu_req_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Request')
    cpu_usage_avg = db.Column(db.Numeric(12, 6), doc='Average Cpu Usage')
    mem_lim_avg = db.Column(db.Numeric(12, 6), doc="Average Memory Limit")
    mem_req_avg = db.Column(db.Numeric(12, 6), doc="Average Memory Request")
    mem_usage_avg = db.Column(db.Numeric(12, 6), doc="Average Memory Usage")

    @hybrid_property
    def pod_num_avg(self):
        return self.pod_num / self.node_num

    @property
    def query_dict(self):
        fields = [
            "cpu_lim_avg", "cpu_req_avg", "cpu_usage_avg", "mem_lim_avg", "mem_req_avg",
            "mem_usage_avg", "pod_num_avg",
        ]
        return {field: getattr(self, field) for field in fields}


class ClusterDeployStrategy(db.Model, Timestamp):
    __status_choices__ = (
        (100, "Active")
    )
    __tablename__ = "cluster_deploy_strategy"
    id = db.Column(db.Integer, primary_key=True, doc='Cluster Deploy Strategy Id')
    name = db.Column(db.String(32), doc="Strategy Name")
    status = db.Column(db.Integer, doc="Strategy Status")
    infix = db.Column(db.String(255), doc=u"Strategy infix")

    @hybrid_property
    def is_default(self):
        return self.name == "default"

    def get_format_str(self):
        return ";\n".join([express.get_format_str() for express in self.expressions])


class StrategyProductConfig(db.Model, Timestamp):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(32), nullable=False, unique=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("cluster_deploy_strategy.id"))
    strategy = db.relation(ClusterDeployStrategy)

    @classmethod
    def get_strategy(cls, product_name: str) -> ClusterDeployStrategy:
        mapping = cls.query.filter(cls.product_name == product_name).first()
        if not mapping:
            return ClusterDeployStrategy.query.filter(ClusterDeployStrategy.is_default).first()
        return mapping.strategy


class StrategyExpression(db.Model, Timestamp):
    __tablename__ = 'expression'
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey("cluster_deploy_strategy.id"))
    strategy = db.relation(ClusterDeployStrategy, backref=db.backref("expressions"))
    infix = db.Column(db.String(255), doc=u"Expression")
    relation_operator = db.Column(db.String(64), doc=u"operator")
    operator_value = db.Column(db.Numeric(12, 6))

    def get_format_str(self):
        return "{} {} {}".format(self.infix, self.relation_operator, self.operator_value)


def create_default_deploy_strategy():
    strategy_name = "default"
    strategy = ClusterDeployStrategy.query.filter(ClusterDeployStrategy.name == strategy_name).first()

    if strategy:
        db.session.delete(strategy)
        db.session.commit()

    # avg_pod_name < 70;
    # avg_cpu < 80 %;
    # avg_mem < 80 %;
    # cpu_request < 80 %;
    # mem_request < 80 %

    strategy = ClusterDeployStrategy(name=strategy_name, status=100, infix=None)

    infix = "pod_num_avg"
    relation_operator = "<="
    operator_value = 70

    expression = StrategyExpression(infix=infix, relation_operator=relation_operator, operator_value=operator_value)
    strategy.expressions.append(expression)

    infix = "cpu_usage_avg"
    relation_operator = "<="
    operator_value = 80

    expression = StrategyExpression(infix=infix, relation_operator=relation_operator, operator_value=operator_value)
    strategy.expressions.append(expression)

    infix = "cpu_req_avg"
    relation_operator = "<"
    operator_value = 80

    expression = StrategyExpression(infix=infix, relation_operator=relation_operator, operator_value=operator_value)
    strategy.expressions.append(expression)

    infix = "mem_req_avg"
    relation_operator = "<"
    operator_value = 80

    expression = StrategyExpression(infix=infix, relation_operator=relation_operator, operator_value=operator_value)
    strategy.expressions.append(expression)

    infix = "mem_usage_avg"
    relation_operator = "<"
    operator_value = 80

    expression = StrategyExpression(infix=infix, relation_operator=relation_operator, operator_value=operator_value)
    strategy.expressions.append(expression)

    db.session.add(strategy)
    db.session.commit()
