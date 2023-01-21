from unicodedata import name

from django.urls import path
from django.urls import include
from rest_framework_simplejwt import views
from rest_framework_nested import routers
from .user_views import *
from .accounts_auth_views import AccountAuthViewSet
from accounts.serializers.serializersNew import myTokenObtainPairSerializer
from .admin_views import AdminViewSet
from accounts.user_views import FollowViewSet

app_name = 'accounts'

router =  routers.DefaultRouter()
router.register('auth', AccountAuthViewSet,
                basename='accounts-auth')
router.register('admin', AdminViewSet, basename='accounts-admin')
router.register('', FollowViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('profile/<username>', UserProfile.as_view(), name='user-profile'),
    path('information', UserInformation.as_view(), name='user-information'),
    path('chat-users', ChatUsers.as_view(), name='chat-users'),
    path('users', GetAllUsers.as_view(), name='user-all'),
    path("auth/signin", views.TokenObtainPairView.as_view(serializer_class=myTokenObtainPairSerializer),
            name="accounts-jwt-create"),
    path("auth/jwt/refresh", views.TokenRefreshView.as_view(),
            name="accounts-jwt-refresh"), 
    path("auth/jwt/verify", views.TokenVerifyView.as_view(),
            name="accounts-jwt-verify"),
#     path(r'^jwt/token/?', views.TokenObtainPairView.as_view(serializer_class=myTokenObtainPairSerializer), name='accounts-jwt-token-new'),
]
