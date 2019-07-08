from aggregation.remote_apps.agent_server.bases import AgentServerAPI


class ClusterAPI(AgentServerAPI):
    name = "cluster"

    def get_cluster_info(self, **kwargs):
        interface = "/cluster_info"
        return self.client.requests(interface=interface, **kwargs)
