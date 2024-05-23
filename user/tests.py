from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


class TestUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@email.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

    def test_follow(self):
        followed_user = get_user_model().objects.create_user(
            email="followed@email.com", password="testpass"
        )

        response = self.client.post(reverse("user:user-detail", args=[followed_user.id]) + "follow-unfollow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_followings_list(self):
        followed_user = get_user_model().objects.create_user(
            email="followed@email.com", password="testpass"
        )
        following_user = get_user_model().objects.create_user(
            email="following@email.com", password="testpass"
        )
        followed_user.followings.add(following_user)
        following_user.followers.add(followed_user)
        response = self.client.get(reverse("user:user-detail", args=[followed_user.id]) + "followers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
