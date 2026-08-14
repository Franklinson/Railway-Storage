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

## Setting up a Railway Bucket

1. On the Railway canvas, right-click an empty area and select **Add Service**
2. Select **Bucket** from the list
3. Click **Deploy** to provision the bucket
4. Navigate to the **Credentials** tab of the bucket
5. Click **Add to Service**
6. Select the service (your Django app) you want to connect the bucket to
7. Under **Style**, select either:
   - **AWS SDK (Generic)** — for general S3-compatible access
   - **Django (django-storages)** — injects variables matching `django-storages` naming
8. The injected environment variables will match what this package expects:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_STORAGE_BUCKET_NAME`
   - `AWS_S3_ENDPOINT_URL`
   - `AWS_S3_REGION_NAME`
9. Click **Add Service** to save — the variables are now available in your Railway deployment

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

Railway injects these automatically when you connect a bucket to your service. Both naming styles are supported:

| Railway Variable | Alternative | Description |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | — | Railway bucket access key |
| `AWS_SECRET_ACCESS_KEY` | — | Railway bucket secret key |
| `AWS_S3_BUCKET_NAME` | `AWS_STORAGE_BUCKET_NAME` | Bucket name |
| `AWS_ENDPOINT_URL` | `AWS_S3_ENDPOINT_URL` | Railway S3-compatible endpoint URL |
| `AWS_DEFAULT_REGION` | `AWS_S3_REGION_NAME` | Region (default: `us-east-1`) |

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
