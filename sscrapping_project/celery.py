# sscrapping_project/celery.py

import os
from celery import Celery

# Setel modul pengaturan default Django untuk program 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sscrapping_project.settings')

app = Celery('sscrapping_project')

# Menggunakan string di sini berarti worker tidak perlu
# serialize objek konfigurasi ke child process.
# - namespace='CELERY' berarti semua kunci konfigurasi Celery
#   harus memiliki awalan `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Muat modul tugas dari semua aplikasi Django yang terdaftar.
app.autodiscover_tasks()