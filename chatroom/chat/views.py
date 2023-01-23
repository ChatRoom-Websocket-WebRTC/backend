from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, permissions, status
from rest_framework import status
from accounts.models import User
from .models import Chat,Group,Message
from .serializers import ChatSerializer,GroupeSeializer,MessageSerializer
import logging

logger = logging.getLogger(__name__)

class ChatAPI(generics.GenericAPIView):
    def get(self, username, room_name):
        usern = User.objects.filter(username=username).first()
        try:
            selectgroup:Group = Group.objects.get(room_name = room_name)
        except:
            return Response({'error': 'group doesnt exist'}, status=status.HTTP_400_BAD_REQUEST)
        return render(username, 'chat/room.html', {
            'room_name': selectgroup.room_name,
        })
    
class GroupAPI(generics.GenericAPIView):
    def get(self, request, room_name, **kwargs):

        group = Group.objects.filter(room_name = room_name).first()
        serializer = GroupeSeializer(group)
        return Response(serializer.data['members'],status=status.HTTP_200_OK)
    
class MessagesAPI(generics.GenericAPIView):
    def get(self, request, room_name, **kwargs):
        messages = Message.objects.filter(group__room_name = room_name)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ChatViewSet(ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    # permission_classes = IsAuthenticated

    @action(
        detail=False,
        methods=['get', 'post'],
        url_path=r'index',
        url_name='chat_index',
        permission_classes=[AllowAny]
    )
    def index(self, request):

        return render(request, 'chat/index.html')

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path=r'room/(?P<room_name>\w+)/username/(?P<username>\w+)',
        url_name='chat_room',
        permission_classes=[AllowAny]
    )
    def room(self, request, room_name, username):

        messages = Chat.objects.filter(room=room_name)

        return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'messages': messages})
    
    @action(
        detail=False,
        methods=['get', 'post'],
        url_path=r'room/messages/(?P<room_name>\w+)',
        url_name='chat_room',
        permission_classes=[AllowAny]
    )
    def get_room_messages(self, request, room_name, *args, **kwargs):
        
        try:
            chats = Chat.objects.filter(room_name=room_name)
            serializer = ChatSerializer(chats, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


def room(request, room_name, username):
    messages = Chat.objects.filter(room_name=room_name)
    return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'messages': messages})