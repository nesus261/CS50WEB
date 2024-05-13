from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    followed = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=2048)
    likes = models.ManyToManyField(User, blank=True, related_name="liked")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content}"