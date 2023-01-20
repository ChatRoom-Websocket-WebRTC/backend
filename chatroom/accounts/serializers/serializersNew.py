from accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model

class myTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            'username': '',
            'password': attrs.get('password')
        }
    
        user_obj = User.objects.filter(email=attrs.get('username')).first() or User.objects.filter(username=attrs.get('username')).first()
        if user_obj:
            credentials['username'] = user_obj.username
            
        return super().validate(credentials)
    
            