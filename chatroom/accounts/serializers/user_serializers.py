from dataclasses import fields
from pyexpat import model
from accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

        
class UserBasicInfoSerializer(serializers.ModelSerializer):
    """Serializer for user basic info """
    class Meta:
        model = User
        fields = ['email', 'username']
   
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    is_owner = serializers.SerializerMethodField('get_is_owner')
    following = serializers.SerializerMethodField('get_following')
    
    
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'image', 'username', 'about_me', 'following_number', 'follower_number', 'following', 'is_owner','is_admin','contact_list']
        read_only_fields = ('email', 'following_number', 'follower_number', 'is_owner','is_admin')
        
    def get_is_owner(self, user):
        request_user = self.context['user']
        if str(request_user) == str(user.username):
            return True
        else:
            return False

    def get_following(self, user):
        status = None
        request_user = self.context['user']
        if request_user.is_authenticated:
            status =  request_user.follows(user) or request_user == user
        return status
    
class UserContactListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['contact_list']

class UserFeedSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField('get_following')

    def get_following(self, user):
        status = None
        request_user = self.context['user']
        if request_user.is_authenticated:
            status =  request_user.follows(user) or request_user == user
        return status
    class Meta:
        model = User
        fields = ['id', 'username', 'image', 'full_name', 'following']
        
        
class UserInformationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'
    

    
    
    
        

