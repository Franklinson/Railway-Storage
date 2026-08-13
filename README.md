# django-railway-storage

A Django package that provides Railway bucket storage backends and a management command to auto-configure your settings.

## Installation

```bash
pip install django-railway-storage
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_railway_storage',
]
```

## Usage

### Auto-configure settings

Run the management command to append the storage config to your settings file:

```bash
# Private storage (presigned URLs, default)
python manage.py configure_railway_storage

# Public storage
python manage.py configure_railway_storage --storage public

# Custom settings file path
python manage.py configure_railway_storage --settings-file config/settings/production.py

# Custom presigned URL expiry (seconds)
python manage.py configure_railway_storage --storage private --expire 7200
```

### Required environment variables

Set these in your Railway project (or `.env`):

| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | Railway bucket access key |
| `AWS_SECRET_ACCESS_KEY` | Railway bucket secret key |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name |
| `AWS_S3_ENDPOINT_URL` | Railway S3-compatible endpoint URL |
| `AWS_S3_REGION_NAME` | Region (default: `us-east-1`) |

### Use backends directly

You can also reference the backends manually in your settings:

```python
# Private (presigned URLs)
STORAGES = {
    "default": {
        "BACKEND": "django_railway_storage.backends.PrivateMediaStorage",
    },
    ...
}

# Public
STORAGES = {
    "default": {
        "BACKEND": "django_railway_storage.backends.PublicMediaStorage",
    },
    ...
}
```

### Use on a model field

```python
from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='documents/')  # uses default storage
```
