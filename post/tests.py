from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Post, Comment, Hashtag


class ViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@email.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

    def test_post_list(self):
        url = reverse("post:post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        post = {
            "author": self.user.id,
            "content": "test",
            "hashtags": [],
            "created_at": timezone.now()
        }
        url = reverse("post:post-list")
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_post(self):
        followed_user = get_user_model().objects.create_user(
            email="followed@email.com", password="testpass"
        )
        post = Post.objects.create(
            author=followed_user,
            content="test"
        )
        self.user.followings.add(followed_user)
        response = self.client.post(reverse("post:post-detail", args=[post.id]) + "like-unlike/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
