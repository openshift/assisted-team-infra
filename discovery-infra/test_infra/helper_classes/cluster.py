import logging

from tests.conftest import env_variables
from test_infra import consts, utils


class Cluster:
    
    def __init__(self, api_client, cluster_name, cluster_id=None):
        self.api_client = api_client

        if cluster_id:
            self.id = cluster_id
        else:
            self.id = self._create(cluster_name).id
    
    def _create(self, cluster_name):
        return self.api_client.create_cluster(
            cluster_name,
            ssh_public_key=env_variables['ssh_public_key'],
            openshift_version=env_variables['openshift_version'],
            pull_secret=env_variables['pull_secret'],
            base_dns_domain=env_variables['base_domain'],
            vip_dhcp_allocation=env_variables['vip_dhcp_allocation']
        )

    def delete(self):
        self.api_client.delete_cluster(self.id)


    def generate_and_download_image(
        self,
        iso_download_path=env_variables['iso_download_path'],
        ssh_key=env_variables['ssh_public_key']
        ):
        self.api_client.generate_and_download_image(
            cluster_id=self.id,
            ssh_key=ssh_key,
            image_path=iso_download_path
        )

    def wait_until_hosts_are_discovered(self,nodes_count=env_variables['num_nodes']):
        utils.wait_till_all_hosts_are_in_status(
            client=self.api_client,
            cluster_id=self.id,
            nodes_count=nodes_count,
            statuses=[consts.NodesStatus.PENDING_FOR_INPUT, consts.NodesStatus.KNOWN]
        )

    def set_host_roles(self):
        utils.set_hosts_roles_based_on_requested_name(
            client=self.api_client,
            cluster_id=self.id
        )

    def set_network_params(
        self, 
        controller,
        nodes_count=env_variables['num_nodes'],
        vip_dhcp_allocation=env_variables['vip_dhcp_allocation'],
        cluster_machine_cidr=env_variables['machine_cidr']
    ):
        if vip_dhcp_allocation:
            self.set_machine_cidr(cluster_machine_cidr)
        else:
            self.set_ingress_and_api_vips(controller)

    def set_machine_cidr(self, machine_cidr):
        logging.info(f'Setting Machine Network CIDR:{machine_cidr} for cluster: {self.id}')
        self.api_client.update_cluster(self.id, {"machine_network_cidr": machine_cidr})

    def set_ingress_and_api_vips(self, controller):
        vips = controller.get_ingress_and_api_vips()
        logging.info(f"Setting API VIP:{vips['api_vip']} and ingres VIP:{vips['ingress_vip']} for cluster: {self.id}")
        self.api_client.update_cluster(self.id, vips)

    def start_install(self):
        self.api_client.install_cluster(cluster_id=self.id)

    def wait_for_installing_in_progress(self, nodes_count=1):
        utils.wait_till_at_least_one_host_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.NodesStatus.INSTALLING_IN_PROGRESS],
            nodes_count=nodes_count
        )

    def wait_for_node_status(self, statuses, nodes_count=1):
        utils.wait_till_at_least_one_host_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=statuses,
            nodes_count=nodes_count
        )

    def wait_for_cluster_in_error_status(self):
        utils.wait_till_cluster_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.ERROR]
        )

    def cancel_install(self):
        self.api_client.cancel_cluster_install(cluster_id=self.id)

    def get_bootstrap_hostname(self):
        hosts = self.get_nodes_by_role(consts.NodeRoles.MASTER)
        for host in hosts:
            if host.get('bootstrap'):
                logging.info("Bootstrap node is: %s", host["requested_hostname"])
                return host["requested_hostname"]

    def get_nodes_by_role(self, role):
        hosts = self.api_client.get_cluster_hosts(self.id)
        nodes_by_role = []
        for host in hosts:
            if host["role"] == role:
                nodes_by_role.append(host)
        logging.info(f"Found hosts: {nodes_by_role}, that has the role: {role}")
        return nodes_by_role

    def get_reboot_required_nodes(self):
        return self.api_client.get_hosts_in_statuses(
            cluster_id=self.id,
            statuses=[consts.NodesStatus.RESETING_PENDING_USER_ACTION]
        )

    def reboot_required_nodes_into_iso_after_reset(self, controller):
        nodes_to_reboot = self.get_reboot_required_nodes()
        for node in nodes_to_reboot:
            node_name = node["requested_hostname"]
            controller.shutdown_node(node_name)
            controller.format_node_disk(node_name)
            controller.start_node(node_name)

    def wait_for_one_host_to_be_in_wrong_boot_order(self, fall_on_error_status=True):
        utils.wait_till_at_least_one_host_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.NodesStatus.INSTALLING_PENDING_USER_ACTION],
            fall_on_error_status=fall_on_error_status,
        )

    def wait_for_ready_to_install(self):
        utils.wait_till_cluster_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.READY]
        )

    def is_in_cancelled_status(self):
        return utils.is_cluster_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.CANCELLED]
        )

    def reset_install(self):
        self.api_client.reset_cluster_install(cluster_id=self.id)

    def is_in_insufficient_status(self):
        return utils.is_cluster_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.INSUFFICIENT]
        )
    
    def wait_for_nodes_to_install(
        self, 
        nodes_count=env_variables['num_nodes'],
        timeout=consts.CLUSTER_INSTALLATION_TIMEOUT
    ):
        utils.wait_till_all_hosts_are_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.INSTALLED],
            nodes_count=nodes_count,
            timeout=timeout,
        )

    def wait_for_install(
        self,  
        timeout=consts.CLUSTER_INSTALLATION_TIMEOUT
    ):
        utils.wait_till_cluster_is_in_status(
            client=self.api_client,
            cluster_id=self.id,
            statuses=[consts.ClusterStatus.INSTALLED],
            timeout=timeout,
        )

    def prepare_for_install(
        self, 
        controller,
        iso_download_path=env_variables['iso_download_path'],
        ssh_key=env_variables['ssh_public_key'],
        nodes_count=env_variables['num_nodes'],
        vip_dhcp_allocation=env_variables['vip_dhcp_allocation'],
        cluster_machine_cidr=env_variables['machine_cidr']
        ):
        self.generate_and_download_image(
            iso_download_path=iso_download_path,
            ssh_key=ssh_key,
        )
        controller.start_all_nodes()
        self.wait_until_hosts_are_discovered(nodes_count=nodes_count)
        self.set_host_roles()
        self.set_network_params(
            controller=controller,
            nodes_count=nodes_count,
            vip_dhcp_allocation=vip_dhcp_allocation,
            cluster_machine_cidr=cluster_machine_cidr
        )
        self.wait_for_ready_to_install()
