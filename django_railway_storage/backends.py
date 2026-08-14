from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


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
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
                config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
            )
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': name},
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
