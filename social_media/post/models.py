import os
import uuid

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from user.models import User


class Hashtag(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


def post_image_file_path(instance, filename: str):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "posts", filename)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_file_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")

    def __str__(self):
        return f"{self.content[15]}... author: {self.author}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.author}: {self.content[:15]}"
