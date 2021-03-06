from abc import ABC
from pathlib import Path
from typing import Any

from dataclasses import dataclass

from test_infra import consts
from test_infra.utils.global_variables import GlobalVariables
from .base_config import _BaseConfig

global_variables = GlobalVariables()


@dataclass
class BaseNodeConfig(_BaseConfig, ABC):
    platform: str = None
    is_ipv6: bool = None   # Todo - Might change during MGMT-5370
    bootstrap_in_place: bool = None
    private_ssh_key_path: Path = None
    working_dir: str = consts.WORKING_DIR

    master_memory: int = None
    master_vcpu: int = None
    masters_count: int = None
    master_cpu_mode: str = None
    master_disk: int = None   # disk size in MB.
    master_disk_size_gib: str = None # disk size in GB.
    master_disk_count: int = None   # number of disks to create

    worker_memory: int = None
    worker_vcpu: int = None
    workers_count: int = None
    worker_cpu_mode: str = None
    worker_disk: int = None
    worker_disk_count: int = None

    network_mtu: int = None

    @staticmethod
    def get_default(key, default=None) -> Any:
        return getattr(global_variables, key)
