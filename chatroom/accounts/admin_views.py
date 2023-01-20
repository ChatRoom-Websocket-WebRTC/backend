import json
from collections import defaultdict
from django.shortcuts import render
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count, Min, Sum

from .models import User
from .serializers.user_serializers import UserProfileSerializer, UserBasicInfoSerializer, UserSerializer
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.test import APIClient
from . permissions import IsAdmin
from accounts.serializers.admin_serilizers import *
from accounts.models import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers



class AdminViewSet(GenericViewSet):
    queryset = User.objects.filter(is_admin=True)

    def get_serializer_class(self):
        return None
    # @action(detail=False, url_path='upgrade-user',  methods=['POST'], permission_classes=[IsAdmin])
    # def UpgradeUser(self, request):
    #     user = User.objects.get(username = request.user.username)
    #     special_user = SpecialUser.objects.create(user = user)
    #     special_user.save()
    #     return Response(f"user with username {request.user.username} upgraded to special user successfully",status = HTTP_200_OK)


    @action(detail=False, url_path='add-admin', methods=['POST'], permission_classes=[permissions.AllowAny])
    def addAdmin(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            user.is_admin = True
            user.save()
            return Response(f'user with username {request.user.username} added as admin', status=status.HTTP_200_OK)
        except:
            return Response(f'unAuthenticated user', status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, url_path='remove-user', methods=['POST'], permission_classes=[IsAdmin])
    def removeUser(self, request):
        try:
            if('username' not in request.data):
                return Response(f'no usernmae is provieded', status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(username=request.data['username'])
            if(user.is_admin):
                return Response(f'admin user can not be removed', status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
            if(user.is_special):
                return Response(f'special user can not be removed', status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
            user.delete()
            return Response(f'user with username {user.username} deleted', status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(f'user with username {user.username} doesn not exist', status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=AddUserSerilizer, responses={
            status.HTTP_200_OK: openapi.Response(
                description="response description",
                schema=UserBasicInfoSerializer,
            )
        })
    @action(detail=False, url_path='add-user', methods=['POST'], permission_classes=[IsAdmin])
    def addUser(self, request):

        if('username' not in request.data):
            return Response(f'no usernmae is provieded', status=status.HTTP_400_BAD_REQUEST)
        if('email' not in request.data):
            return Response(f'no email is provieded', status=status.HTTP_400_BAD_REQUEST)
        if('password' not in request.data):
            return Response(f'no password is provieded', status=status.HTTP_400_BAD_REQUEST)
        if(request.data['re_password'] != request.data['password']):
            return Response(f'password and re_password are not same', status=status.HTTP_400_BAD_REQUEST)

        client = APIClient()
        url = reverse('accounts:accounts-auth-check-username')
        response = client.post(url, json.dumps(
            {"username": request.data['username']}), content_type='application/json')
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return Response(f'username already exists', status=status.HTTP_400_BAD_REQUEST)

        url = reverse('accounts:accounts-auth-check-email')
        response = client.post(url, json.dumps(
            {"email": request.data['email']}), content_type='application/json')
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return Response(f'email already exists', status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=request.data['username'], email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        serializer = UserBasicInfoSerializer(data=request.data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    