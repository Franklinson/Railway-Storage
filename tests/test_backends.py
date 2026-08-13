import os
import tempfile
from unittest.mock import MagicMock, patch
from io import StringIO

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError


BASE_SETTINGS = dict(
    AWS_ACCESS_KEY_ID='test-key',
    AWS_SECRET_ACCESS_KEY='test-secret',
    AWS_STORAGE_BUCKET_NAME='test-bucket',
    AWS_S3_ENDPOINT_URL='https://s3.example.com',
    AWS_S3_REGION_NAME='us-east-1',
)


@override_settings(**BASE_SETTINGS)
class PrivateMediaStorageTests(TestCase):
    def _get_storage(self):
        from django_railway_storage.backends import PrivateMediaStorage
        return PrivateMediaStorage()

    @patch('django_railway_storage.backends.boto3.client')
    def test_url_returns_presigned_url(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://signed.url/file.jpg'
        mock_boto_client.return_value = mock_s3

        storage = self._get_storage()
        url = storage.url('file.jpg')

        self.assertEqual(url, 'https://signed.url/file.jpg')
        mock_s3.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'file.jpg'},
            ExpiresIn=3600,
        )

    @patch('django_railway_storage.backends.boto3.client')
    def test_url_respects_custom_expire(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://signed.url/file.jpg'
        mock_boto_client.return_value = mock_s3

        storage = self._get_storage()
        storage.url('file.jpg', expire=7200)

        _, kwargs = mock_s3.generate_presigned_url.call_args
        self.assertEqual(kwargs['ExpiresIn'], 7200)

    @patch('django_railway_storage.backends.boto3.client')
    def test_url_falls_back_on_client_error(self, mock_boto_client):
        from botocore.exceptions import ClientError
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {'Error': {'Code': '403', 'Message': 'Forbidden'}}, 'get_object'
        )
        mock_boto_client.return_value = mock_s3

        storage = self._get_storage()
        with patch.object(storage.__class__.__bases__[0], 'url', return_value='https://fallback.url/file.jpg'):
            url = storage.url('file.jpg')
        self.assertEqual(url, 'https://fallback.url/file.jpg')


@override_settings(**BASE_SETTINGS)
class PublicMediaStorageTests(TestCase):
    def test_storage_attributes(self):
        from django_railway_storage.backends import PublicMediaStorage
        storage = PublicMediaStorage()
        self.assertEqual(storage.default_acl, 'public-read')
        self.assertEqual(storage.location, 'media/public')
        self.assertFalse(storage.file_overwrite)
        self.assertFalse(storage.custom_domain)


class ConfigureRailwayStorageCommandTests(TestCase):
    def _run(self, settings_file, **kwargs):
        out = StringIO()
        call_command('configure_railway_storage', settings_file=settings_file, stdout=out, **kwargs)
        return out.getvalue()

    def test_appends_private_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# existing settings\n')
            path = f.name
        try:
            output = self._run(path)
            with open(path) as f:
                content = f.read()
            self.assertIn('PrivateMediaStorage', content)
            self.assertIn('AWS_ACCESS_KEY_ID', content)
            self.assertIn('Railway Storage', output)
        finally:
            os.unlink(path)

    def test_appends_public_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# existing settings\n')
            path = f.name
        try:
            self._run(path, storage='public')
            with open(path) as f:
                content = f.read()
            self.assertIn('PublicMediaStorage', content)
        finally:
            os.unlink(path)

    def test_raises_if_already_configured(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# django-railway-storage\n')
            path = f.name
        try:
            with self.assertRaises(CommandError):
                self._run(path)
        finally:
            os.unlink(path)

    def test_raises_if_file_not_found(self):
        with self.assertRaises(CommandError):
            self._run('/nonexistent/settings.py')

    def test_custom_expire(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# existing settings\n')
            path = f.name
        try:
            self._run(path, expire=7200)
            with open(path) as f:
                content = f.read()
            self.assertIn('7200', content)
        finally:
            os.unlink(path)
