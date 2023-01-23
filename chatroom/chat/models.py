from django.db import models
from accounts.models import User
# Create your models here.


class Chat(models.Model):
    
    class SenderType(models.TextChoices):
        server = 'SERVER'
        Client = 'CLIENT'
    
    sender = models.ForeignKey(
        User, related_name='send_chats', on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=250)
    sender_type= models.CharField(max_length=6, choices=SenderType.choices, null=True)

class Group(models.Model):
    room_name = models.CharField(max_length=250)
    members = models.ManyToManyField(User)

class Message(models.Model):
    class MessageType(models.TextChoices):
        file = 'FILE'
        text = 'TEXT'
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=483647)
    message_type = models.CharField(max_length=4,choices=MessageType.choices, null=False)
    file_extension = models.CharField(max_length=255, blank=True, null=True)
