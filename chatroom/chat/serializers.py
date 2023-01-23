from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from .models import Chat,Message,Group
from accounts.models import User

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class GroupeSeializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(many=False, slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['sender', 'group', 'message','message_type', 'file_extension']
