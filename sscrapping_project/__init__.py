# sscrapping_project/__init__.py

# Baris ini memastikan app selalu diimpor saat Django dimulai
# sehingga @shared_task akan menggunakan app ini.
from .celery import app as celery_app

__all__ = ('celery_app',)