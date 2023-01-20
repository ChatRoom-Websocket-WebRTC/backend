from accounts.models import *
from rest_framework import serializers



class RemoveUserSerilizer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    
class AddUserSerilizer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)