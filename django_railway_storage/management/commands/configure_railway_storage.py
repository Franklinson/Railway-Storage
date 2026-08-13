from django.core.management.base import BaseCommand, CommandError
import os


SETTINGS_SNIPPET = '''
# --- django-railway-storage ---
import os

STORAGES = {{
    "default": {{
        "BACKEND": "{backend}",
    }},
    "staticfiles": {{
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }},
}}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = {querystring_auth}
AWS_QUERYSTRING_EXPIRE = {querystring_expire}
AWS_S3_FILE_OVERWRITE = False
AWS_S3_SIGNATURE_VERSION = 's3v4'
MEDIA_URL = f'{{AWS_S3_ENDPOINT_URL}}/{{AWS_STORAGE_BUCKET_NAME}}/'
AWS_S3_OBJECT_PARAMETERS = {{'CacheControl': 'max-age=86400'}}
# --- end django-railway-storage ---
'''

BACKENDS = {
    'private': 'django_railway_storage.backends.PrivateMediaStorage',
    'public': 'django_railway_storage.backends.PublicMediaStorage',
}


class Command(BaseCommand):
    help = 'Append Railway Storage configuration to your settings file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--settings-file',
            default='settings.py',
            help='Path to your Django settings file (default: settings.py)',
        )
        parser.add_argument(
            '--storage',
            choices=['private', 'public'],
            default='private',
            help='Storage type: private (presigned URLs) or public (default: private)',
        )
        parser.add_argument(
            '--expire',
            type=int,
            default=3600,
            help='Presigned URL expiry in seconds, only used for private storage (default: 3600)',
        )

    def handle(self, *args, **options):
        settings_path = options['settings_file']

        if not os.path.isabs(settings_path):
            settings_path = os.path.join(os.getcwd(), settings_path)

        if not os.path.exists(settings_path):
            raise CommandError(f'Settings file not found: {settings_path}')

        with open(settings_path, 'r') as f:
            content = f.read()

        if 'django-railway-storage' in content:
            raise CommandError('Railway Storage config already exists in the settings file.')

        storage_type = options['storage']
        backend = BACKENDS[storage_type]
        querystring_auth = storage_type == 'private'
        expire = options['expire']

        snippet = SETTINGS_SNIPPET.format(
            backend=backend,
            querystring_auth=querystring_auth,
            querystring_expire=expire,
        )

        with open(settings_path, 'a') as f:
            f.write(snippet)

        self.stdout.write(self.style.SUCCESS(
            f'Railway Storage ({storage_type}) config appended to {settings_path}.\n'
            'Make sure to set the required environment variables:\n'
            '  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,\n'
            '  AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL, AWS_S3_REGION_NAME'
        ))
