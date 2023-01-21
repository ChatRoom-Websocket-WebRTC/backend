from rest_framework.response import Response
from .models import User
from .serializers.user_serializers import *
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from chat.models import Chat


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UserProfile(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, username, *args, **kwargs):
        parser_classes = [MultiPartParser, FormParser]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(
            user, context={'user': request.user})
        return Response(serializer.data)

    def put(self, request, username, *args, **kwargs):
        parser_classes = [MultiPartParser, FormParser]
        user = User.objects.get(username=username)
        # if(request.user != username):
        # 	return Response("token is not for given username", status=status.HTTP_400_BAD_REQUEST)
        # else:
        serializer = UserProfileSerializer(
            user, data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Contacts(GenericAPIView):
    def get(self,request,username):
        try:
            user = User.objects.get(username=username)
        except Exception:
            return Response({"error":"user does not exists"},status=status.HTTP_400_BAD_REQUEST)
        serializer = UserContactListSerializer(user)
        contacts = str(serializer.data['contact_list'])
        contacts = contacts.split(",")
        contacts_list = {}
        counter = 0
        for contact in contacts:
            contact = User.objects.get(id = contact)
            contacts_list[counter] = ({"username":contact.username,"phone":contact.phone_no,"email":contact.email,"firstname":contact.first_name,"lastname":contact.last_name,"last_login":contact.last_login})
            counter += 1
        print(contacts_list)
        return Response(contacts_list, status=status.HTTP_200_OK)
        

class FollowViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserFeedSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[AllowAny],
            url_name="get-followers", url_path="followers")
    def get_followers(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserFeedSerializer(
            user.followers, context={'user': request.user}, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, permission_classes=[AllowAny],
            url_name="get-following", url_path="following")
    def get_following(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserFeedSerializer(
            user.following, context={'user': request.user}, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['post'])
    def follow(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.follows(user):
            return Response("you already follows this user.",
                            status=status.HTTP_400_BAD_REQUEST)
        request.user.following.add(user)
        user.update_follower_no()
        request.user.update_following_no()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['post'])
    def unfollow(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.follows(user):
            return Response("you are not following this user.",
                            status=status.HTTP_400_BAD_REQUEST)
        request.user.following.remove(user)
        user.update_follower_no()
        request.user.update_following_no()
        return Response(status=status.HTTP_200_OK)


class UserInformation(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        request_user = request.user
        print(f"{request.user}")
        try:
            username = request_user.username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInformationSerializer(user)
        return Response(serializer.data)



class GetAllUsers(GenericAPIView):

    queryset = User.objects.all()
    serializer_class = None
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=None, responses={
    status.HTTP_200_OK: openapi.Response(
        description="response description",
        schema=UserSerializer,
    )
})
    def get(self, request, *args, **kwargs):

        try:
            users = self.get_queryset()
            serializer = UserSerializer(users,many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
class ChatUsers(GenericAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        chats = Chat.objects.all()
        usernames = []
        users = []
        for chat in chats:
            if chat.room_name not in usernames:
                usernames.append(chat.room_name)
                user = User.objects.get(username=chat.room_name)
                # user_information.append(user.username)
                users.append(user)
                # if user.image != None and user.image != "":
                #     user_information.append(user.image)
                # else:
                #     user_information.append("")
            #     response[user.pk] = user_information
            #     i += 1
            # print(chat.room_name)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        