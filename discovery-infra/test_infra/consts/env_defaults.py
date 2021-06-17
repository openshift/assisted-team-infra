from pathlib import Path

from test_infra import consts


DEFAULT_NUMBER_OF_MASTERS: int = consts.NUMBER_OF_MASTERS
DEFAULT_DAY2_WORKERS_COUNT: int = 0
DEFAULT_WORKERS_COUNT: int = 0
DEFAULT_STORAGE_POOL_PATH: Path = Path.cwd().joinpath("storage_pool")
DEFAULT_SSH_PRIVATE_KEY_PATH: Path = Path.cwd().joinpath("ssh_key/key")
DEFAULT_INSTALLER_KUBECONFIG = None
DEFAULT_LOG_FOLDER: Path = Path("/tmp/assisted_test_infra_logs")
DEFAULT_SERVICE_CIDR: str = "172.30.0.0/16"
DEFAULT_CLUSTER_CIDR: str = "10.128.0.0/14"
DEFAULT_HOST_PREFIX: int = 23
DEFAULT_IMAGE_TYPE: str = consts.ImageType.FULL_ISO
DEFAULT_TEST_TEARDOWN: bool = True
DEFAULT_PLATFORM: str = consts.Platforms.BARE_METAL
DEFAULT_USER_MANAGED_NETWORKING: bool = False
DEFAULT_HIGH_AVAILABILITY_MODE: str = consts.HighAvailabilityMode.FULL
DEFAULT_DOWNLOAD_IMAGE: bool = True
DEFAULT_IS_IPV6: bool = False
DEFAULT_ADDITIONAL_NTP_SOURCE: str = consts.DEFAULT_ADDITIONAL_NTP_SOURCE
DEFAULT_IS_STATIC_IP: bool = False
DEFAULT_BOOTSTRAP_IN_PLACE: bool = False
DEFAULT_NETWORK_NAME: str = consts.TEST_NETWORK
DEFAULT_SINGLE_NODE_IP: str = ""
DEFAULT_TF_CPU_MODE: str = consts.HOST_PASSTHROUGH_CPU_MODE
DEFAULT_IMAGE_FOLDER: Path = Path(consts.IMAGE_FOLDER)
DEFAULT_IMAGE_FILENAME: str = "installer-image.iso"
DEFAULT_KUBECONFIG_DIR: Path = Path("/tmp/kubeconfig")
