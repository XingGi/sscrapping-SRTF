# core/urls.py

from django.urls import path
from .views import VideoListAPIView, CommentListAPIView, start_youtube_scrape, start_comment_scrape

urlpatterns = [
    path('videos/', VideoListAPIView.as_view(), name='video-list'),
    path('comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('scrape/youtube/', start_youtube_scrape, name='scrape-youtube'),
    path('scrape/comments/', start_comment_scrape, name='scrape-comments'),
]