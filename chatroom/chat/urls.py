from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import *
from . import views 

app_name = 'chat'

router = routers.DefaultRouter()
router.register('', ChatViewSet, basename='chat')




urlpatterns = [
    path('', include(router.urls)),
    path('room/<str:room_name>/username/<str:username>', views.room, name='room')
]
