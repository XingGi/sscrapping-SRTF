# core/models.py

from django.db import models

class Video(models.Model):
    """
    Model ini merepresentasikan satu video yang di-scrape.
    Setiap baris di tabel ini adalah satu video unik.
    """
    channel_name = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    video_url = models.URLField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        # Mengurutkan video berdasarkan tanggal pembuatan terbaru
        ordering = ['-created_at']
        # Memberi nama tabel yang lebih baik di database
        verbose_name_plural = "Videos"


class Comment(models.Model):
    """
    Model ini merepresentasikan satu komentar dari sebuah video.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    username = models.CharField(max_length=255)
    text = models.TextField()
    comment_url = models.URLField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.username} on {self.video.title}'

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Comments"