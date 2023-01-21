from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(
        upload_to='images/users/', blank=True, null=True)
    phone_no = models.CharField(max_length=11, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    following = models.ManyToManyField(
        'User', related_name='followers', blank=True)
    following_number = models.IntegerField(default=0)
    follower_number = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False, blank=True)
    contact_list = models.CharField(default="",blank=True,max_length=1024)
    
    def follows(self, user):
        return user in self.following.all()

    def update_follower_no(self):
        self.follower_number = self.followers.count()
        self.save()

    def update_following_no(self):
        self.following_number = self.following.count()
        self.save()


class Verification(models.Model):
    email = models.EmailField(primary_key=True)
    username = models.CharField(max_length=255)
    token = models.CharField(max_length=6)
    password = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Token(models.Model):
    uid = models.CharField(primary_key=True, max_length=100)
    token = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

