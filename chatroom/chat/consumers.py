import json

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from accounts.models import User
from .models import Chat,Group,Message

class ChatConsumer(WebsocketConsumer):
    
    def create_chat(self, id, message,room_name,username,message_type):
        selectgroup = Group.objects.get(room_name = room_name)
        if 'user' not in self.scope.keys():
            self.scope['user'] = User.objects.get(username=username)
        new_msg = Message.objects.create(sender=self.scope['user'], message=message, group=selectgroup,message_type = message_type)
        new_msg.save()

    def get_all_messages(self):
        name = self.scope['url_route']['kwargs']['room_name']
        select_room = Group.objects.get(room_name = name)
        messages = Message.objects.filter(group = select_room)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)
            
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message:Message):
        # print (message.sender.userprofile.avatar)
        return {
            'id': message.id,
            'username' :message.sender.username,
            'message': message.message,
            'message_type':message.message_type
        }

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.get_all_messages()


            

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        message = text_data_json['message']
        username = text_data_json['username']
        roon_name = text_data_json['room_name']
        self.scope['user'] = User.objects.get(username=username)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'id': self.scope['user'].id,
                'username' : username
            }
        )
        new_msg = self.create_chat(id, message,roon_name,username)

    # Receive message from room group
    def chat_message(self, event):
        if ('message' not in event):
            raise Exception('no message_exception')
        message = event['message']
        group = event['room_name']
        username = event['username']


        # Send message to WebSocket
        data = {
            'message': message,
            'username': username
        }
        self.send(text_data=json.dumps(data))