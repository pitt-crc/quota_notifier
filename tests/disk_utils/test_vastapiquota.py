"""Tests for the ``VastApiQuota`` class"""

import secrets
from pathlib import Path
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pydantic import SecretStr

from quota_notifier.disk_utils import QuotaFactory, VastApiQuota
from quota_notifier.settings import ApplicationSettings
from quota_notifier.shell import User
from tests.base import DefaultSetupTeardown

TEST_TOKEN = secrets.token_hex(8)
TEST_PASSWORD = secrets.token_hex(8)

TEST_RECORDS = [
    {'path': '/ihome/group/user1', 'hard_limit': 1000, 'soft_limit': 0, 'used_capacity': 250},
    {'path': '/ihome/group/user2/', 'hard_limit': 0, 'soft_limit': 500, 'used_capacity': 100},
    {'path': '/ihome/group/user3', 'hard_limit': 0, 'soft_limit': 0, 'used_capacity': 100},
]


def mock_get_quotas(path: Optional[str] = None) -> list[dict]:
    """Mimic the VAST API filtering quota records by path"""

    if path is None:
        return TEST_RECORDS

    return [record for record in TEST_RECORDS if record['path'].rstrip('/') == path]


class VastApiTestBase(DefaultSetupTeardown):
    """Mock the VAST API client and reset cached quota data"""

    def setUp(self) -> None:
        """Mock API responses and clear cached quota data"""

        super().setUp()
        VastApiQuota._cached_quotas = None

        self.mock_client = MagicMock()
        self.mock_client.quotas.get.side_effect = mock_get_quotas
        self.client_patcher = patch.object(VastApiQuota, '_get_client', return_value=self.mock_client)
        self.client_patcher.start()

    def tearDown(self) -> None:
        """Stop API mocking and clear cached quota data"""

        self.client_patcher.stop()
        VastApiQuota._cached_quotas = None
        super().tearDown()


class GetQuota(VastApiTestBase, TestCase):
    """Test fetching individual quotas via the ``get_quota`` method"""

    def test_quota_values(self) -> None:
        """Test the returned quota reflects usage reported by the API"""

        quota = VastApiQuota.get_quota('ihome', Path('/ihome/group/user1'), User('root'))
        self.assertEqual(250, quota.size_used)
        self.assertEqual(1000, quota.size_limit)
        self.assertEqual(25, quota.percentage)

    def test_soft_limit_fallback(self) -> None:
        """Test the soft limit is used when no hard limit is set"""

        quota = VastApiQuota.get_quota('ihome', Path('/ihome/group/user2'), User('root'))
        self.assertEqual(500, quota.size_limit)

    def test_no_limit_returns_none(self) -> None:
        """Test ``None`` is returned for quotas with no limit set"""

        self.assertIsNone(VastApiQuota.get_quota('ihome', Path('/ihome/group/user3'), User('root')))

    def test_missing_quota_returns_none(self) -> None:
        """Test ``None`` is returned for paths without a quota"""

        self.assertIsNone(VastApiQuota.get_quota('ihome', Path('/ihome/group/fake'), User('root')))

    def test_factory_returns_api_quota(self) -> None:
        """Test the ``QuotaFactory`` uses the VAST API for ihome file systems"""

        quota = QuotaFactory('ihome', 'ihome', Path('/ihome/group/user1'), User('root'))
        self.assertIsInstance(quota, VastApiQuota)


class CacheQuotas(VastApiTestBase, TestCase):
    """Test bulk caching via the ``cache_quotas`` method"""

    def test_cached_values(self) -> None:
        """Test cached quotas are keyed by normalized path and exclude quotas without limits"""

        VastApiQuota.cache_quotas()
        self.assertEqual(
            {'/ihome/group/user1': (250, 1000), '/ihome/group/user2': (100, 500)},
            VastApiQuota._cached_quotas)

    def test_cache_is_used(self) -> None:
        """Test ``get_quota`` does not query the API once quotas are cached"""

        VastApiQuota.cache_quotas()
        self.mock_client.quotas.get.reset_mock()

        quota = VastApiQuota.get_quota('ihome', Path('/ihome/group/user1'), User('root'))
        self.assertEqual(250, quota.size_used)
        self.assertIsNone(VastApiQuota.get_quota('ihome', Path('/ihome/group/fake'), User('root')))
        self.mock_client.quotas.get.assert_not_called()


class GetClient(DefaultSetupTeardown, TestCase):
    """Test the ``VASTClient`` is configured from application settings"""

    def test_token_credentials(self) -> None:
        """Test the API token is passed to the client when configured"""

        ApplicationSettings.set(vast_host='vms.domain.com', vast_token=SecretStr(TEST_TOKEN))
        with patch('quota_notifier.disk_utils.VASTClient') as mock_client:
            VastApiQuota._get_client()

        mock_client.assert_called_once_with(address='vms.domain.com', cert_file=None, token=TEST_TOKEN)

    def test_password_credentials(self) -> None:
        """Test the username and password are passed to the client when no token is configured"""

        ApplicationSettings.set(
            vast_host='vms.domain.com', vast_user='user', vast_password=SecretStr(TEST_PASSWORD),
            vast_ca_cert=Path('/ca.pem'))

        with patch('quota_notifier.disk_utils.VASTClient') as mock_client:
            VastApiQuota._get_client()

        mock_client.assert_called_once_with(address='vms.domain.com', cert_file='/ca.pem', user='user',
                                            password=TEST_PASSWORD)
