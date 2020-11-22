import pytest
import time
import logging

from test_infra import consts
from tests.base_test import BaseTest
from tests.conftest import env_variables


logger = logging.getLogger(__name__)


@pytest.mark.wrong_boot_order
class TestWrongBootOrder(BaseTest):
    @pytest.mark.regression
    def test_wrong_boot_order_one_node(self, nodes, cluster):
        # Define new cluster
        new_cluster = cluster()

        # Change boot order of a random node
        node = nodes.get_random_node()
        node.set_boot_order(cd_first=True)

        # Start cluster install
        new_cluster.prepare_for_install(nodes)
        new_cluster.start_install()
        new_cluster.wait_for_installing_in_progress()

        # Wait until wrong boot order
        new_cluster.wait_for_one_host_to_be_in_wrong_boot_order()
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Reboot required nodes into HD
        node.shutdown()
        node.set_boot_order(cd_first=False)
        node.start()

        # wait until all nodes are in Installed status, will fail in case one host in error
        new_cluster.wait_for_cluster_to_be_in_installing_status()
        new_cluster.wait_for_hosts_to_install()
        new_cluster.wait_for_install()

    @pytest.mark.regression
    def test_installation_succeeded_after_all_nodes_have_incorrect_boot_order(self,
                                                                              nodes,
                                                                              cluster):
        # Define new cluster
        new_cluster = cluster()

        # Change boot order of all the nodes
        for n in nodes:
            n.set_boot_order(cd_first=True)

        # Start cluster install
        new_cluster.prepare_for_install(nodes)
        new_cluster.start_install()
        new_cluster.wait_for_installing_in_progress()

        # Wait until wrong boot order - all hosts except bootstrap
        new_cluster.wait_for_hosts_to_be_in_wrong_boot_order(len(nodes)-1)
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Reboot required nodes into HD
        bootstrap = nodes.get_bootstrap_node(cluster=new_cluster)
        for n in nodes:
            if n.name == bootstrap.name:
                continue
            n.shutdown()
            n.set_boot_order(cd_first=False)
            n.start()

        # Wait until installation continued.
        new_cluster.wait_for_cluster_to_be_in_installing_status()

        # Wait until bootstrap is in wrong boot order
        new_cluster.wait_for_one_host_to_be_in_wrong_boot_order()
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Reboot bootstrap into HD
        bootstrap.shutdown()
        bootstrap.set_boot_order(cd_first=False)
        bootstrap.start()

        new_cluster.wait_for_cluster_to_be_in_installing_status()
        new_cluster.wait_for_hosts_to_install()
        new_cluster.wait_for_install()

    @pytest.mark.regression
    def test_reset_cancel_from_incorrect_boot_order(self, nodes, cluster):
        # Define new cluster
        new_cluster = cluster()

        # Change boot order of all the nodes
        for n in nodes:
            n.set_boot_order(cd_first=True)

        # Start cluster install
        new_cluster.prepare_for_install(nodes)
        new_cluster.start_install()
        new_cluster.wait_for_installing_in_progress()

        # Wait until wrong boot order - all hosts except bootstrap
        new_cluster.wait_for_hosts_to_be_in_wrong_boot_order(nodes_count=env_variables['num_masters']-1)
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Cancel and reset installation
        new_cluster.cancel_install()
        assert new_cluster.is_in_cancelled_status(), \
            f'cluster {new_cluster.id} failed to cancel installation'
        new_cluster.reset_install()
        assert new_cluster.is_in_insufficient_status(), \
            f'cluster {new_cluster.id} failed to reset installation'

        # Reboot required nodes into HD
        nodes.set_correct_boot_order(start_nodes=False)
        new_cluster.reboot_required_nodes_into_iso_after_reset(
            nodes=nodes)

        # Install Cluster
        new_cluster.wait_until_hosts_are_discovered()
        new_cluster.wait_for_ready_to_install()
        # new_cluster.start_install()
        # new_cluster.wait_for_hosts_to_install()
        # new_cluster.wait_for_install()

    @pytest.mark.regression
    def test_installation_succeeded_on_incorrect_boot_order_timeout_is_ignored(self,
                                                                               nodes,
                                                                               cluster):
        # Define new cluster
        new_cluster = cluster()

        # Change boot order all the nodes
        for n in nodes:
            n.set_boot_order(cd_first=True)

        # Start cluster install
        new_cluster.prepare_for_install(nodes)
        new_cluster.start_install()
        new_cluster.wait_for_installing_in_progress()

        # Wait until wrong boot order - all hosts except bootstrap
        new_cluster.wait_for_hosts_to_be_in_wrong_boot_order(len(nodes)-1)
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Wait for an hour+, in normal cases we expect to get timeout error
        # after an hour
        logger.info('Waiting 65 minutes before fixing wrong boot order')
        time.sleep(65 * 60)

        # Reboot required nodes into HD
        bootstrap = nodes.get_bootstrap_node(cluster=new_cluster)
        for n in nodes:
            if n.name == bootstrap.name:
                continue
            n.shutdown()
            n.set_boot_order(cd_first=False)
            n.start()

        # Wait until installation continued.
        new_cluster.wait_for_cluster_to_be_in_installing_status()
        
        # Wait until bootstrap is in wrong boot order
        new_cluster.wait_for_one_host_to_be_in_wrong_boot_order()
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()

        # Reboot bootstrap into HD
        bootstrap.shutdown()
        bootstrap.set_boot_order(cd_first=False)
        bootstrap.start()

        # Wait until installation continued.
        new_cluster.wait_for_cluster_to_be_in_installing_status()
        new_cluster.wait_for_hosts_to_install()
        new_cluster.wait_for_install()

    @pytest.mark.regression
    def test_cluster_state_move_from_incorrect_boot_to_error(self, nodes, cluster):
        # Define new cluster
        new_cluster = cluster()
        # Change boot order to all masters
        master_nodes = nodes.get_masters()
        nodes.set_wrong_boot_order(master_nodes, False)
        # Start cluster install
        new_cluster.prepare_for_install(nodes=nodes)
        new_cluster.start_install()
        new_cluster.wait_for_installing_in_progress()
        # Wait until one host is in wrong boot order
        new_cluster.wait_for_one_host_to_be_in_wrong_boot_order()
        new_cluster.wait_for_cluster_to_be_in_installing_pending_user_action_status()
        # Kill bootstrap installer to simulate cluster error
        bootstrap = nodes.get_bootstrap_node(cluster=new_cluster)
        bootstrap.kill_podman_container_by_name("assisted-installer")
        # Wait for node and cluster Error
        new_cluster.wait_for_host_status([consts.NodesStatus.ERROR])
        new_cluster.wait_for_cluster_in_error_status()
        # Reset cluster install
        new_cluster.reset_install()
        assert new_cluster.is_in_insufficient_status()
        # Fix boot order and reboot required nodes into ISO
        nodes.set_correct_boot_order(master_nodes, False)
        new_cluster.reboot_required_nodes_into_iso_after_reset(nodes=nodes)
        # Wait for hosts to be rediscovered
        new_cluster.wait_until_hosts_are_discovered()
        new_cluster.wait_for_ready_to_install()
        # Install Cluster and wait until all nodes are in Installed status
        # new_cluster.start_install_and_wait_for_installed()
