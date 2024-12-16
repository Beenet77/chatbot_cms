from rest_framework import serializers
from .models import CMSContent, ChatMessage

class CMSContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSContent
        fields = ['key', 'value', 'language']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['user_message', 'bot_response', 'timestamp']
