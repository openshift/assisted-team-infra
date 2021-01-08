import logging
import pytest
import json
import os
from contextlib import suppress
from typing import Optional
from pathlib import Path
from paramiko import SSHException

from test_infra import consts
import test_infra.utils as infra_utils
from test_infra.tools.assets import NetworkAssets
from test_infra.controllers.proxy_controller.proxy_controller import ProxyController
from assisted_service_client.rest import ApiException
from test_infra.helper_classes.cluster import Cluster
from test_infra.helper_classes.nodes import Nodes
from tests.conftest import env_variables, qe_env
from download_logs import download_logs


class BaseTest:

    @pytest.fixture(scope="function")
    def nodes(self, setup_node_controller):
        net_asset = None
        try:
            if not qe_env:
                net_asset = NetworkAssets()
                env_variables["net_asset"] = net_asset.get()
            controller = setup_node_controller(**env_variables)
            nodes = Nodes(controller, env_variables["private_ssh_key_path"])
            nodes.prepare_nodes()
            yield nodes
            logging.info('--- TEARDOWN --- node controller\n')
            nodes.destroy_all_nodes()
        finally:
            if not qe_env:
                net_asset.release_all()

    @pytest.fixture()
    def cluster(self, api_client, request, nodes):
        clusters = []

        def get_cluster_func(cluster_name: Optional[str] = None,
                             additional_ntp_source: Optional[str] = consts.DEFAULT_ADDITIONAL_NTP_SOURCE,
                             openshift_version: Optional[str] = env_variables['openshift_version']):
            if not cluster_name:
                cluster_name = infra_utils.get_random_name(length=10)

            res = Cluster(api_client=api_client,
                          cluster_name=cluster_name,
                          additional_ntp_source=additional_ntp_source,
                          openshift_version=openshift_version)
            clusters.append(res)
            return res

        yield get_cluster_func

        for cluster in clusters:
            logging.info(f'--- TEARDOWN --- Collecting Logs for test: {request.node.name}\n')
            self.collect_test_logs(cluster, api_client, request.node, nodes)
            logging.info(f'--- TEARDOWN --- deleting created cluster {cluster.id}\n')
            if cluster.is_installing() or cluster.is_finalizing():
                cluster.cancel_install()

            with suppress(ApiException):
                cluster.delete()

    @pytest.fixture()
    def iptables(self):
        rules = []

        def set_iptables_rules_for_nodes(
            cluster, 
            nodes,
            given_nodes,
            iptables_rules,  
            download_image=True,
            iso_download_path=env_variables['iso_download_path'],
            ssh_key=env_variables['ssh_public_key']
            ):
            given_node_ips=[]
            if download_image:
                cluster.generate_and_download_image(
                    iso_download_path=iso_download_path,
                    ssh_key=ssh_key
                )
                nodes.start_given(given_nodes)
                for node in given_nodes:
                    given_node_ips.append(node.ips[0])
                nodes.shutdown_given(given_nodes)
            else:
                for node in given_nodes:
                    given_node_ips.append(node.ips[0])

            logging.info(f'Given node ips: {given_node_ips}')

            for rule in iptables_rules:
                rule.add_sources(given_node_ips)
                rules.append(rule)
                rule.insert()

        yield set_iptables_rules_for_nodes
        logging.info('---TEARDOWN iptables ---')
        for rule in rules:
            rule.delete()

    @pytest.fixture(scope="function")
    def attach_disk(self):
        modified_node = None

        def attach(node, disk_size):
            nonlocal modified_node
            node.attach_test_disk(disk_size)
            modified_node = node

        yield attach

        if modified_node is not None:
            modified_node.detach_all_test_disks()

    @pytest.fixture()
    def proxy_server(self):
        logging.info('--- SETUP --- proxy controller')
        proxy_servers = []

        def start_proxy_server(**kwargs):
            proxy_server = ProxyController(**kwargs)
            proxy_servers.append(proxy_server)

            return proxy_server

        yield start_proxy_server
        logging.info('--- TEARDOWN --- proxy controller')
        for server in proxy_servers:
            server.remove()

    @staticmethod
    def get_cluster_by_name(api_client, cluster_name):
        clusters = api_client.clusters_list()
        for cluster in clusters:
            if cluster['name'] == cluster_name:
                return cluster
        return None

    @staticmethod
    def assert_http_error_code(api_call, status, reason, **kwargs):
        with pytest.raises(ApiException) as response:
            api_call(**kwargs)
        assert response.value.status == status
        assert response.value.reason == reason

    @staticmethod
    def assert_cluster_validation(cluster_info, validation_section, validation_id, expected_status):
        found_status = infra_utils.get_cluster_validation_value(cluster_info, validation_section, validation_id)
        assert found_status == expected_status, "Found validation status " + found_status + " rather than " +\
                                                expected_status + " for validation " + validation_id

    @staticmethod
    def assert_string_length(string, expected_len):
        assert len(string) == expected_len, "Expected len string of: " + str(expected_len) + \
                                            " rather than: " + str(len(string)) + " String value: " + string

    def collect_test_logs(self, cluster, api_client, test, nodes):
        log_dir_name = f"{env_variables['log_folder']}/{test.name}"
        with suppress(ApiException):
            cluster_details = json.loads(json.dumps(cluster.get_details().to_dict(), sort_keys=True, default=str))
            download_logs(api_client, cluster_details, log_dir_name, test.result_call.failed)
        if test.result_call.failed:
            self._collect_virsh_logs(nodes, log_dir_name)
            self._collect_journalctl(nodes, log_dir_name)

    def _collect_virsh_logs(self, nodes, log_dir_name):
        logging.info('Collecting virsh logs\n')
        os.makedirs(log_dir_name, exist_ok=True)
        virsh_log_path = os.path.join(log_dir_name, "libvirt_logs")
        os.makedirs(virsh_log_path, exist_ok=False)

        libvirt_list_path = os.path.join(virsh_log_path, "virsh_list")
        infra_utils.run_command(f"virsh list --all >> {libvirt_list_path}", shell=True)

        libvirt_net_list_path = os.path.join(virsh_log_path, "virsh_net_list")
        infra_utils.run_command(f"virsh net-list --all >> {libvirt_net_list_path}", shell=True)

        network_name = nodes.get_cluster_network()
        virsh_leases_path = os.path.join(virsh_log_path, "net_dhcp_leases")
        infra_utils.run_command(f"virsh net-dhcp-leases {network_name} >> {virsh_leases_path}", shell=True)

        messages_log_path = os.path.join(virsh_log_path, "messages.log")
        infra_utils.run_command(f"cp -p /var/log/messages {messages_log_path}", shell=True)

        qemu_libvirt_path = os.path.join(virsh_log_path, "qemu_libvirt_logs")
        os.makedirs(qemu_libvirt_path, exist_ok=False)
        for node in nodes:
            infra_utils.run_command(f"cp -p /var/log/libvirt/qemu/{node.name}.log "
                                    f"{qemu_libvirt_path}/{node.name}.log",
                                    shell=True)

        libvird_log_path = os.path.join(virsh_log_path, "libvirtd_journal")
        infra_utils.run_command(f"journalctl --since \"{nodes.setup_time}\" "
                                f"-u libvirtd -D /run/log/journal >> {libvird_log_path}", shell=True)

    def _collect_journalctl(self, nodes, log_dir_name):
        logging.info('Collecting journalctl\n')
        infra_utils.recreate_folder(log_dir_name, with_chmod=False ,force_recreate=False)
        journal_ctl_path = Path(log_dir_name) / 'nodes_journalctl'
        infra_utils.recreate_folder(journal_ctl_path, with_chmod=False)
        for node in nodes:
            try:
                node.run_command(f'sudo journalctl >> /tmp/{node.name}-journalctl')
                journal_path = journal_ctl_path / node.name
                node.download_file(f'/tmp/{node.name}-journalctl', str(journal_path))
            except (RuntimeError, TimeoutError, SSHException):
                logging.info(f'Could not collect journalctl for {node.name}')

    @staticmethod
    def verify_no_logs_uploaded(cluster, cluster_tar_path):
        with pytest.raises(ApiException) as ex:
            cluster.download_installation_logs(cluster_tar_path)
        assert "No log files" in str(ex.value)

    def update_oc_config(self, nodes, cluster):
        os.environ["KUBECONFIG"] = env_variables['kubeconfig_path']
        vips = nodes.controller.get_ingress_and_api_vips()
        api_vip = vips['api_vip']
        infra_utils.config_etc_hosts(cluster_name=cluster.name,
                               base_dns_domain=env_variables["base_domain"],
                               api_vip=api_vip)
