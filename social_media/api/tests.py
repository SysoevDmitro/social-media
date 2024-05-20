# tests/test_posts.py

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Post, Comment

User = get_user_model()

class PostTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpass')
        self.post = Post.objects.create(author=self.user, content='Test Post')

    def test_like_post(self):
        self.client.login(email='testuser@gmail.com', password='testpass')
        response = self.client.post(f'/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.likes.count(), 1)
        self.client.logout()

    def test_comment_post(self):
        self.client.login(email='testuser@gmail.com', password='testpass')
        response = self.client.post(f'/posts/{self.post.id}/comment/', {'content': 'Test Comment'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.client.logout()

    def test_post_likes_and_comments_count(self):
        self.client.login(email='testuser@gmail.com', password='testpass')
        self.client.post(f'/posts/{self.post.id}/like/')
        self.client.post(f'/posts/{self.post.id}/comment/', {'content': 'Test Comment'})
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['likes_count'], 1)
        self.assertEqual(response.data[0]['comments_count'], 1)
        self.client.logout()
