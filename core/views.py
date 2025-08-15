# core/views.py

from rest_framework import generics, filters # Pastikan 'filters' sudah diimpor
from .models import Video, Comment
from .serializers import VideoSerializer, CommentSerializer

class VideoListAPIView(generics.ListAPIView):
    """
    API view untuk menampilkan daftar semua video,
    dengan kemampuan filtering dan searching.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    
    # Baris-baris ini sekarang akan bekerja karena 'filters' sudah diimpor
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'channel_name']
    ordering_fields = ['created_at', 'channel_name']
    
class CommentListAPIView(generics.ListAPIView):
    """
    API view untuk menampilkan daftar semua komentar dengan filter dan pencarian.
    """
    queryset = Comment.objects.select_related('video').all()
    serializer_class = CommentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'text', 'video__title'] # Cari berdasarkan username, isi komentar, atau judul video
    ordering_fields = ['created_at', 'username']