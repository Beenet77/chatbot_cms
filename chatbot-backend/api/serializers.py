from rest_framework import serializers
from .models import CMSContent, ChatMessage , Logo
class CMSContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSContent
        fields = ['key', 'value', 'language']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['user_message', 'bot_response', 'timestamp']

class LogoSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Logo
        fields = ['id', 'logo']

    def get_logo_url(self, obj):
        # Construct the full URL for the image
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logo.url)