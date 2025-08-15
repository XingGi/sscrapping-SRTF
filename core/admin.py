# core/admin.py

from django.contrib import admin
from .models import Video, Comment # Import model Anda

# Buat class untuk kustomisasi tampilan di admin
class VideoAdmin(admin.ModelAdmin):
    # Menampilkan kolom-kolom ini di daftar video
    list_display = ('title', 'channel_name', 'created_at')
    # Menambahkan filter di sisi kanan
    list_filter = ('channel_name',)
    # Menambahkan bar pencarian
    search_fields = ('title', 'channel_name')

# Daftarkan model Video dengan kustomisasi di atas
admin.site.register(Video, VideoAdmin)

# Daftarkan juga model Comment (untuk nanti)
admin.site.register(Comment)