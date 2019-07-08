from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase


class RemoteClientTestCase(AggregationAuthorizedTestCase):

    def test_get_attribute(self):
        from aggregation.remote_apps.agent_server.apis import ClusterAPI
        from aggregation.remote_apps.agent_server.bases import AgentServerClient
        from aggregation.api.modules.cluster.models import Cluster

        cluster = Cluster()
        client = AgentServerClient(cluster=cluster)

        def call():
            print(client.hello_world)

        self.assertRaises(AttributeError, call)
        api = client.api_cluster
        print(api, ClusterAPI)
        print(isinstance(api, ClusterAPI))
        self.assertEqual(isinstance(api, ClusterAPI), True)

