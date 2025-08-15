# core/serializers.py

from rest_framework import serializers
from .models import Video, Comment

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'channel_name', 'title', 'video_url', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'video', 'username', 'text', 'comment_url', 'created_at']