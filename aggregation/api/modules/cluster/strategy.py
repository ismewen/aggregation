from typing import List

from aggregation.api.modules.cluster.models import ClusterDeployStrategy, Cluster


class DeployClusterStrategy(object):

    def __init__(self, package_name: str, region: str):
        self.package_name = package_name
        self.region = region
        self.strategy = self.get_strategy(package_name)

    def get_strategy(self, package_name) -> ClusterDeployStrategy:
        pass

    def get_current_region_clusters(self) -> List[Cluster]:
        pass

    def who_is_best_cluster(self) -> Cluster:
        pass
