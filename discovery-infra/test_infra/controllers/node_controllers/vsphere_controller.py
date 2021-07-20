import os
from builtins import list
from typing import Tuple, List, Callable, Any

import libvirt

from test_infra.controllers.node_controllers.disk import Disk
from test_infra.controllers.node_controllers.node import Node
from test_infra.controllers.node_controllers.node_controller import NodeController
from test_infra.helper_classes.config import BaseClusterConfig
from test_infra.helper_classes.config.vsphere_config import VSphereControllerConfig
from test_infra.tools import terraform_utils
from test_infra.utils.terraform_util import TerraformControllerUtil


class VSphereController(NodeController):

    def __init__(self, config: VSphereControllerConfig, cluster_config: BaseClusterConfig):
        super().__init__(config, cluster_config)
        self.cluster_name = cluster_config.cluster_name.get()
        folder = TerraformControllerUtil.create_folder(self.cluster_name, platform=cluster_config.platform)
        self._tf = terraform_utils.TerraformUtils(working_dir=folder)

    def prepare_nodes(self):
        config = {**self._config.get_all(), **self._cluster_config.get_all(),
                  "cluster_name": self.cluster_name}
        # The ISO file isn't available now until preparing for installation
        del config["iso_download_path"]
        self._tf.set_and_apply(**config)
        return self.list_nodes()

    def iso_ready(self):
        config = {**self._config.get_all(), **self._cluster_config.get_all(), "cluster_name": self.cluster_name}
        self._tf.set_and_apply(**config)

    def start_node(self, node_name: str, check_ips: bool) -> None:
        pass

    def list_nodes(self) -> List[Node]:
        vms = self.__get_vms()

        def vsphere_vm_to_node(terraform_vm_state):
            return Node(name=terraform_vm_state["attributes"]["name"],
                        private_ssh_key_path=self._config.private_ssh_key_path,
                        node_controller=self)

        return list(map(vsphere_vm_to_node, vms))

    def get_cpu_cores(self, node_name: str) -> int:
        return self.__get_vm(node_name)["attributes"]["num_cpus"]

    def get_ram_kib(self, node_name: str) -> int:
        return self.__get_vm(node_name)["attributes"]["memory"] * 1024

    def destroy_all_nodes(self) -> None:
        self._tf.destroy()

    def start_all_nodes(self) -> List[Node]:
        raise NotImplementedError

    def shutdown_node(self, node_name: str) -> None:
        raise NotImplementedError

    def shutdown_all_nodes(self) -> None:
        raise NotImplementedError

    def restart_node(self, node_name: str) -> None:
        raise NotImplementedError

    def format_node_disk(self, node_name: str, disk_index: int = 0) -> None:
        raise NotImplementedError

    def list_disks(self, node_name: str) -> List[Disk]:
        raise NotImplementedError

    def is_active(self, node_name) -> bool:
        raise NotImplementedError

    def get_node_ips_and_macs(self, node_name) -> Tuple[List[str], List[str]]:
        raise NotImplementedError

    def format_all_node_disks(self) -> None:
        raise NotImplementedError

    def list_networks(self) -> List[Any]:
        raise NotImplementedError

    def list_leases(self, network_name: str) -> List[Any]:
        raise NotImplementedError

    def attach_test_disk(self, node_name: str, disk_size: int, bootable=False, persistent=False, with_wwn=False):
        raise NotImplementedError

    def detach_all_test_disks(self, node_name: str):
        raise NotImplementedError

    def get_ingress_and_api_vips(self) -> dict:
        raise NotImplementedError

    def get_cluster_network(self) -> str:
        raise NotImplementedError

    def setup_time(self) -> str:
        raise NotImplementedError

    def set_boot_order(self, node_name, cd_first=False) -> None:
        raise NotImplementedError

    def set_per_device_boot_order(self, node_name, key: Callable[[Disk], int]) -> None:
        raise NotImplementedError

    def get_host_id(self, node_name: str) -> str:
        raise NotImplementedError

    def set_cpu_cores(self, node_name: str, core_count: int) -> None:
        raise NotImplementedError

    def set_ram_kib(self, node_name: str, ram_kib: int) -> None:
        raise NotImplementedError

    def get_machine_cidr(self) -> str:
        raise NotImplementedError

    def attach_interface(self, node_name, network_xml: str) -> Tuple[libvirt.virNetwork, str]:
        raise NotImplementedError

    def add_interface(self, node_name, network_name, target_interface: str) -> str:
        raise NotImplementedError

    def undefine_interface(self, node_name: str, mac: str):
        raise NotImplementedError

    def create_network(self, network_xml: str) -> libvirt.virNetwork:
        raise NotImplementedError

    def get_network_by_name(self, network_name: str) -> libvirt.virNetwork:
        raise NotImplementedError

    def destroy_network(self, network: libvirt.virNetwork):
        raise NotImplementedError

    def set_single_node_ip(self, ip):
        raise NotImplementedError

    def __get_vm(self, node_name):
        return next((vm for vm in self.__get_vms() if vm["attributes"]["name"] == node_name), None)

    def __get_vms(self):
        vms_object_type = self._tf.get_resources(resource_type="vsphere_virtual_machine")

        if not vms_object_type:
            return list()

        return vms_object_type[0]["instances"]
