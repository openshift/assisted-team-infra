TF_FOLDER = "build/terraform"
TFVARS_JSON_NAME = "terraform.tfvars.json"
IMAGE_FOLDER = "/tmp/test_images"
TF_MAIN_JSON_NAME = "main.tf"
BASE_IMAGE_FOLDER = "/tmp/images"
IMAGE_NAME = "installer-image.iso"
STORAGE_PATH = "/var/lib/libvirt/openshift-images"
SSH_KEY = "ssh_key/key.pub"
NODES_REGISTERED_TIMEOUT = 60 * 20
CLUSTER_INSTALLATION_TIMEOUT = 60 * 60  # 60 minutes
CLUSTER_INSTALLATION_TIMEOUT_OCS = 60 * 95
START_CLUSTER_INSTALLATION_TIMEOUT = 360
INSTALLING_IN_PROGRESS_TIMEOUT = 60 * 10
VALIDATION_TIMEOUT = 6 * 60
NTP_VALIDATION_TIMEOUT = 10 * 60
OCS_VALIDATION_TIMEOUT = 10 * 60
CNV_VALIDATION_TIMEOUT = 10 * 60
WORKER_CPU = 2
MASTER_CPU = 4
READY_TIMEOUT = 60 * 15
DISCONNECTED_TIMEOUT = 60 * 10
PENDING_USER_ACTION_TIMEOUT = 60 * 30
ERROR_TIMEOUT = 60 * 10
TF_TEMPLATE_BARE_METAL_FLOW = "terraform_files/baremetal"
TF_TEMPLATE_NONE_PLATFORM_FLOW = "terraform_files/none"
TF_NETWORK_POOL_PATH = "/tmp/tf_network_pool.json"
NUMBER_OF_MASTERS = 3
TEST_INFRA = "test-infra"
CLUSTER = CLUSTER_PREFIX = "%s-cluster" % TEST_INFRA
TEST_NETWORK = "test-infra-net-"
TEST_SECONDARY_NETWORK = "test-infra-secondary-network-"
DEFAULT_CLUSTER_KUBECONFIG_PATH = "build/kubeconfig"
WAIT_FOR_BM_API = 900
NAMESPACE_POOL_SIZE = 15
PODMAN_FLAGS = "--cgroup-manager=cgroupfs --storage-driver=vfs --events-backend=file"
LOG_FOLDER = "/tmp/assisted_test_infra_logs"
DEFAULT_OPENSHIFT_VERSION = "4.7"
DEFAULT_ADDITIONAL_NTP_SOURCE = "clock.redhat.com"
DEFAULT_BASE_DNS_DOMAIN = "redhat.com"
DEFAULT_NAMESPACE = 'assisted-installer'
DEFAULT_TEST_INFRA_DOMAIN = f".{CLUSTER_PREFIX}-{DEFAULT_NAMESPACE}.{DEFAULT_BASE_DNS_DOMAIN}"
TEST_TARGET_INTERFACE = "vnet3"
RANGE_8BIT = 2 ** 8
RANGE_16BIT = 2 ** 16


class ImageType:
    FULL_ISO = "full-iso"
    MINIMAL_ISO = "minimal-iso"


class NodeRoles:
    WORKER = "worker"
    MASTER = "master"
    AUTO_ASSIGN = "auto-assign"


class NodesStatus:
    INSUFFICIENT = "insufficient"
    KNOWN = "known"
    INSTALLING = "installing"
    INSTALLING_IN_PROGRESS = "installing-in-progress"
    INSTALLING_PENDING_USER_ACTION = "installing-pending-user-action"
    INSTALLED = "installed"
    ERROR = "error"
    PENDING_FOR_INPUT = "pending-for-input"
    DAY2_INSTALLED = "added-to-existing-cluster"
    RESETING_PENDING_USER_ACTION = "resetting-pending-user-action"
    DISCONNECTED = "disconnected"


class ClusterStatus:
    INSUFFICIENT = "insufficient"
    INSTALLED = "installed"
    READY = "ready"
    PREPARING_FOR_INSTALLATION = "preparing-for-installation"
    INSTALLING = "installing"
    FINALIZING = "finalizing"
    ERROR = "error"
    PENDING_FOR_INPUT = "pending-for-input"
    CANCELLED = "cancelled"
    INSTALLING_PENDING_USER_ACTION = "installing-pending-user-action"


class HostsProgressStages:
    START_INSTALLATION = "Starting installation"
    INSTALLING = "Installing"
    WRITE_IMAGE_TO_DISK = "Writing image to disk"
    WAIT_FOR_CONTROL_PLANE = "Waiting for control plane"
    REBOOTING = "Rebooting"
    WAIT_FOR_IGNITION = "Waiting for ignition"
    JOINED = "Joined"
    CONFIGURING = "Configuring"
    DONE = "Done"


all_host_stages = [HostsProgressStages.START_INSTALLATION, HostsProgressStages.INSTALLING,
                   HostsProgressStages.WRITE_IMAGE_TO_DISK, HostsProgressStages.WAIT_FOR_CONTROL_PLANE,
                   HostsProgressStages.REBOOTING, HostsProgressStages.WAIT_FOR_IGNITION,
                   HostsProgressStages.CONFIGURING, HostsProgressStages.JOINED, HostsProgressStages.DONE]


class Events:
    REGISTERED_CLUSTER = "Registered cluster"
    SUCCESSFULLY_REGISTERED_CLUSTER = "Successfully registered cluster"
    PENDING_FOR_INPUT = "to pending-for-input"
    GENERATED_IMAGE = "Generated image (SSH public key is set)"
    GENERATED_IMAGE_FULL = "Generated image (Image type is \"full-iso\", SSH public key is set)"
    GENERATED_IMAGE_MINIMAL = "Generated image (Image type is \"minimal-iso\", SSH public key is set)"
    DOWNLOAD_IMAGE = "Started image download"
    STARTED_DOWNLOAD_IMAGE = "Started image download (image type is \"full-iso\")"
    HOST_REGISTERED_TO_CLUSTER = ": registered to cluster"
    INSUFFICIENT = "insufficient"
    KNOWN = "to \"known\""
    READY = "to ready"
    CLUSTER_VALIDATION = "Cluster validation \'all-hosts-are-ready-to-install\' is now fixed"
    PREPARING_FOR_INSTALLATION = "updated status from \"known\" to \"preparing-for-installation\""
    PREPARING_SUCCESSFUL = "updated status from \"preparing-for-installation\" to \"preparing-successful\""
    SET_BOOTSTRAP = "set as bootstrap"
    INSTALLING = "updated status from \"preparing-successful\" to \"installing\""
    CLUSTER_PREPARED = "Cluster was prepared successfully for installation"
    CLUSTER_INSTALLING = "to installing"
    INSTALLING_IN_PROGRESS = "updated status from \"installing\" to \"installing-in-progress\""
    INSTALLATION_STAGE = "reached installation stage Starting installation"
    INSTALLING_PENDING_USER_ACTION = "installing-pending-user-action"
    WRITING_IMAGE_TO_DISK = "reached installation stage Writing image to disk"
    REBOOTING = "reached installation stage Rebooting"
    CONTROL_PLANE = "reached installation stage Waiting for control plane"
    IGNITION = "reached installation stage Waiting for ignition"
    CONFIGURING = "reached installation stage Configuring"
    JOINED = "reached installation stage Joined"
    DONE = "reached installation stage Done"
    CANCELLED_CLUSTER_INSTALLATION = "Cancelled cluster installation"
    CANCELLED_FOR_HOST = "Installation cancelled for host"
    CLUSTER_VERSION_DONE = "Cluster version status: available message: Done"
    CANCELLED_STATUS = "to \"cancelled\""
    RESET_CLUSTER_INSTALLATION = "Reset cluster installation"
    RESET_FOR_HOST = "Installation reset for host"
    RESETTING_PENDING_USER_ACTION = "updated status from \"cancelled\" to \"resetting-pending-user-action\""
    INSTALLED = "updated status from \"installing-in-progress\" to \"installed\""
    FINALIZING = "to finalizing"
    SUCCESSFULLY_INSTALLED = "Successfully finished installing cluster"
    ERROR = "error"
    DAY2_INSTALLED = "added-to-existing-cluster"
    PROXY_SETTINGS_CHANGED = "Proxy settings changed"


class Platforms:
    BARE_METAL = 'baremetal'
    NONE = 'none'


class HighAvailabilityMode:
    FULL = 'Full'
    NONE = 'None'
