from .controller_config import BaseControllerConfig
from dataclasses import dataclass


@dataclass
class VSphereControllerConfig(BaseControllerConfig):
    def get_copy(self):
        return VSphereControllerConfig(**self.get_all())

    vsphere_vcenter: str = None
    vsphere_username: str = None
    vsphere_password: str = None
    vsphere_cluster: str = None
    vsphere_datacenter: str = None
    vsphere_datastore: str = None
    vsphere_network: str = None

    def __post_init__(self):
        super().__post_init__()
