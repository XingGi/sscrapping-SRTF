# core/urls.py

from django.urls import path
from .views import VideoListAPIView, CommentListAPIView

urlpatterns = [
    path('videos/', VideoListAPIView.as_view(), name='video-list'),
    path('comments/', CommentListAPIView.as_view(), name='comment-list'),
]