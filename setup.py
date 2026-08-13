from setuptools import setup, find_packages

setup(
    name='django-railway-storage',
    version='1.0.0',
    description='Django storage backends and auto-configuration for Railway bucket storage.',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'django>=3.2',
        'django-storages[s3]>=1.13',
        'boto3>=1.20',
        'botocore>=1.23',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
