from django.conf import settings
from rest_framework.decorators import action
from rest_framework import permissions, status
from rest_framework.response import Response
from validate_email import validate_email
import random
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from accounts.models import User, Verification, Token
from rest_framework_simplejwt import views
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime, timedelta, timezone
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from .serializers.user_serializers import *
from .models import User

from drf_yasg.utils import swagger_auto_schema


class check_email_seriliazer(serializers.Serializer):
    email = serializers.CharField(max_length=50, help_text="user email")


class check_username_seriliazer(serializers.Serializer):
    username = serializers.CharField(max_length=50, help_text="user username")


class check_code_seriliazer(serializers.Serializer):
    email = serializers.CharField(max_length=50, help_text="user email")
    token = serializers.CharField(max_length=6, help_text="sent token")


class activate_seriliazer(serializers.Serializer):
    email = serializers.CharField(max_length=50, help_text="user email")
    username = serializers.CharField(max_length=50, help_text="user username")


class set_password_seriliazer(serializers.Serializer):
    username = serializers.CharField(max_length=50, help_text="user username")
    password = serializers.CharField(max_length=50, help_text="user password")
    re_password = serializers.CharField(max_length=50, help_text="user re_password")
    email = serializers.CharField(max_length=50, help_text="user email")
    token = serializers.CharField(max_length=6, help_text="sent token")


class reset_password_seriliazer(serializers.Serializer):
    email = serializers.CharField(max_length=50, help_text="user email")


class reset_password_confirm_seriliazer(serializers.Serializer):
    token = serializers.CharField(max_length=50, help_text="sent token")
    password = serializers.CharField(max_length=50, help_text="user password")
    uid = serializers.CharField(max_length=50)


class AccountAuthViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=check_email_seriliazer)
    @action(detail=False, url_path='check-email', methods=['POST'], permission_classes=[permissions.AllowAny])
    def check_email(self, request):
        if request.method == 'POST':
            try:
                User.objects.get(email=request.data['email'])
                return Response(f"email '{request.data['email']}' already exists!",
                                status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK, data='New Email')

    def remove_expired_token_uids(self, request):
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        Token.objects.filter(create_time__lte=time_threshold).delete()

    @action(detail=False, url_path='activation-email', methods=['POST'], permission_classes=[permissions.AllowAny])
    def ActivationEmail(self, request):
        if request.method == 'POST':
            # remove_expired_tokens()
            user_email = request.data['email']
            user_username = request.data['username']
            user_password = request.data['password1']

            if validate_email(user_email):

                otp = str(random.randint(100000, 999999))
                email_title = "تایید حساب کاربری"
                template = render_to_string(
                    'activation.html',
                    {
                        'username': user_username,
                        'otp': otp,
                        'WEBSITE_URL': 'chatroom.ir',
                    }
                )
                email_from = settings.EMAIL_HOST_USER
                email_to = user_email

                email = EmailMessage(email_title,
                                     template,
                                     email_from,
                                     [email_to]
                                     )

                email.content_subtype = "html"
                email.fail_silently = False
                email.send()

                try:
                    # email resent
                    verification_obj = Verification.objects.get(
                        email=user_email)
                    verification_obj.token = str(otp)
                    verification_obj.username = user_username
                    verification_obj.save()

                except Verification.DoesNotExist:
                    # email sent
                    verification_obj = Verification.objects.create(
                        email=user_email,
                        password=user_password,
                        username=user_username,
                        token=str(otp))
                    verification_obj.save()

                return Response(status=status.HTTP_200_OK, data='Email sent successfully')
                # return Response({"code": random_code}, status= status.HTTP_200_OK)

            else:
                return Response(f"'{user_email}' doesn't exist", status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=check_username_seriliazer)
    @action(detail=False, url_path='check-username', methods=['POST'], permission_classes=[permissions.AllowAny])
    def check_username(self, request):
        if request.method == 'POST':
            try:
                User.objects.get(username=request.data['username'])
                return Response(f"username '{request.data['username']}' is already taken!",
                                status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK, data='New Username')

    @swagger_auto_schema(request_body=activate_seriliazer)
    @action(detail=False, url_path='activate', methods=['POST'], permission_classes=[permissions.AllowAny])
    def activate(self, request):

        if request.method == 'POST':

            if (self.check_username(request).status_code == 400):
                return Response(f"username '{request.data['username']}' already exists!",
                                status=status.HTTP_400_BAD_REQUEST)

            if (self.check_email(request).status_code == 400):
                return Response(f"email '{request.data['email']}' is already taken!",
                                status=status.HTTP_400_BAD_REQUEST)

            return self.ActivationEmail(request)

    @swagger_auto_schema(request_body=set_password_seriliazer)
    @action(detail=False, url_path='signup_otp', methods=['POST'], permission_classes=[permissions.AllowAny])
    def signup_otp(self, request):
        if request.method == 'POST':
            try:
                unregistered_user = Verification.objects.get(
                    email=request.data['email'])
            except Verification.DoesNotExist:
                return Response(f"user with email '{request.data['email']}' doesn't exist",
                                status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(f"no email sent",
                                status=status.HTTP_400_BAD_REQUEST)

            if (unregistered_user.token == request.data['token']):
                user = User.objects.create(
                    username=unregistered_user.username, email=unregistered_user.email)
                user.set_password(unregistered_user.password)
                user.save()
                unregistered_user.delete()
                return Response(f"registered successfully",
                                status=status.HTTP_201_CREATED)

            else:
                return Response(f"otp is invalid",
                                status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=set_password_seriliazer)
    @action(detail=False, url_path='resend_otp', methods=['POST'], permission_classes=[permissions.AllowAny])
    def resend_otp(self, request):
        unregistered_user = Verification.objects.get(email=request.data['email'])
        otp = str(random.randint(100000, 999999))
        unregistered_user.token = str(otp)
        unregistered_user.save()
        email_title = "تایید حساب کاربری"
        template = render_to_string(
            'activation.html',
            {
                'username': unregistered_user.username,
                'otp': otp,
                'WEBSITE_URL': 'chatroom.ir',
            }
        )
        email_from = settings.EMAIL_HOST_USER
        email_to = unregistered_user.email

        email = EmailMessage(email_title,
                             template,
                             email_from,
                             [email_to]
                             )

        email.content_subtype = "html"
        email.fail_silently = False
        email.send()
        return Response(status=status.HTTP_200_OK, data='Email sent successfully')


    @swagger_auto_schema(request_body=reset_password_seriliazer)
    @action(detail=False, url_path='reset-password', methods=['POST'], permission_classes=[permissions.AllowAny])
    def reset_pass_email(self, request):
        self.remove_expired_token_uids(request)
        user_email = request.data['email']
        # if validate_email(user_email):
        try:
            user = User.objects.get(email=request.data['email'])
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            template = render_to_string('reset_password.html',
                                        {
                                            'user': user,
                                            'token': token,
                                            'uid': uid,
                                            'host': request.get_host(),
                                            'port': request.get_port()
                                        })

            email = EmailMessage('بازنشانی رمز عبور در چت‌روم',
                                 template,
                                 settings.EMAIL_HOST_USER,
                                 [user_email]
                                 )

            email.content_subtype = "html"
            email.fail_silently = False
            email.send()

            try:
                token_obj = Token.objects.get(uid=uid)
                token_obj.token = str(token)
                token_obj.save()

            except Token.DoesNotExist:
                token_obj = Token.objects.create(
                    token=str(token), uid=str(uid))
                token_obj.save()
            return Response(status=status.HTTP_200_OK, data='Email sent successfully')

        except User.DoesNotExist:
            return Response(f"user with email {user_email} doesn't exist!",
                            status=status.HTTP_404_NOT_FOUND)
        # else:
        #     return Response(f"'{user_email}' is not a valid email.",
        #                                 status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=reset_password_confirm_seriliazer)
    @action(detail=False, url_path='reset-password/confirm', methods=['POST'],
            permission_classes=[permissions.AllowAny])
    def reset_pass_confirm(self, request, *args, **kwargs):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('password')

        if uid is None or not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='uid is not Provided')
        if token is None or not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='token is not Provided')

        try:
            token_obj = Token.objects.get(uid=uid)
            if token_obj.token == token:
                user = User.objects.get(pk=urlsafe_base64_decode(uid))
                if user.username != new_password:
                    user.set_password(new_password)
                    user.save()
                    token_obj.delete()
                    return Response(status=status.HTTP_200_OK,
                                    data='password successfuly changed.')
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data='password cannot be the same as username.')
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='incorrect token.')

        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="token doesn't exist.")
