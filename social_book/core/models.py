from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank_profile_picture.png')
    location = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=128)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    num_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return "{} ({})".format(self.user, self.created_at)

class LikePost(models.Model):
    post_id = models.CharField(max_length=512)
    username = models.CharField(max_length=128)

    def __str__(self):
        return self.username + " -> " + self.post_id
