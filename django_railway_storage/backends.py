from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import boto3
import os
from botocore.exceptions import ClientError


def _get_setting(django_setting, *env_keys, default=None):
    """Read from Django settings first, then fall back to Railway env var names."""
    value = getattr(settings, django_setting, None)
    if value:
        return value
    for key in env_keys:
        value = os.environ.get(key)
        if value:
            return value
    return default


class PrivateMediaStorage(S3Boto3Storage):
    location = ''
    default_acl = None
    file_overwrite = False
    custom_domain = False
    querystring_auth = True
    querystring_expire = 3600
    addressing_style = 'path'

    def url(self, name, parameters=None, expire=None, http_method=None):
        if expire is None:
            expire = self.querystring_expire
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=_get_setting('AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=_get_setting('AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY'),
                endpoint_url=_get_setting('AWS_S3_ENDPOINT_URL', 'AWS_ENDPOINT_URL'),
                region_name=_get_setting('AWS_S3_REGION_NAME', 'AWS_DEFAULT_REGION', default='us-east-1'),
                config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
            )
            bucket = _get_setting('AWS_STORAGE_BUCKET_NAME', 'AWS_S3_BUCKET_NAME')
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': name},
                ExpiresIn=expire,
            )
        except ClientError:
            return super().url(name, parameters, expire, http_method)


class PublicMediaStorage(S3Boto3Storage):
    location = 'media/public'
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = False
    addressing_style = 'path'
