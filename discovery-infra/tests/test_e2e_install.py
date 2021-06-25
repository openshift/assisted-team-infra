import pytest
from junit_report import JunitTestSuite
from test_infra.consts import OperatorStatus

from tests.base_test import BaseTest
from tests.config import ClusterConfig, TerraformConfig
from tests.conftest import get_available_openshift_versions, get_api_client


class TestInstall(BaseTest):

    @JunitTestSuite()
    @pytest.mark.parametrize("openshift_version", sorted(get_available_openshift_versions()))
    def test_install(self, get_nodes, get_cluster, openshift_version):
        new_cluster = get_cluster(cluster_config=ClusterConfig(openshift_version=openshift_version), nodes=get_nodes())
        new_cluster.prepare_for_installation()
        new_cluster.start_install_and_wait_for_installed()

    @JunitTestSuite()
    @pytest.mark.parametrize("olm_operator", sorted(get_api_client().get_supported_operators()))
    def test_olm_operator(self, get_nodes, get_cluster, olm_operator):
        new_cluster = get_cluster(cluster_config=ClusterConfig(olm_operators=[olm_operator]),
                                  nodes=get_nodes(TerraformConfig(olm_operators=[olm_operator])))
        new_cluster.prepare_for_installation()
        new_cluster.start_install_and_wait_for_installed()
        assert new_cluster.is_operator_in_status(olm_operator, OperatorStatus.AVAILABLE)
