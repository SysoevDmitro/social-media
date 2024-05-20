from django.db import models
from django.conf import settings
from django.utils.text import slugify
import pathlib
import uuid
from user.models import User


def post_picture_path(instance, filename: str) -> pathlib.Path:
    return pathlib.Path("upload/" + instance.__class__.__name__.lower()) / pathlib.Path(
        f"{slugify(filename)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    )


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    media = models.ImageField(upload_to=post_picture_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="user_likes")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"post id={self.id} | " f"{self.created_at} | {self.content[:15]} ..."


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"comment id={self.id} | " f"{self.created_at} | {self.content[:15]}"
