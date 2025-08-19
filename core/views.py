# core/views.py

from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Video, Comment
from .serializers import VideoSerializer, CommentSerializer
from .tasks import scrape_youtube_videos_task

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
    
@api_view(['POST'])
def start_youtube_scrape(request):
    """
    API endpoint untuk memulai proses scraping YouTube.
    Menerima 'keyword' dari body permintaan.
    """
    keyword = request.data.get('keyword', None)

    if not keyword:
        return Response({'error': 'Keyword is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Memanggil task Celery untuk berjalan di latar belakang
    # .delay() adalah cara untuk memberitahu Celery agar menjalankan task ini
    scrape_youtube_videos_task.delay(keyword=keyword)

    return Response(
        {'status': 'success', 'message': f"Proses scraping untuk keyword '{keyword}' telah dimulai di latar belakang."},
        status=status.HTTP_202_ACCEPTED
    )