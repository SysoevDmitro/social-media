from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsAuthorOrIfAuthenticatedReadOnly
from .models import User

from .serializers import (
    UserSerializer,
    UserListSerializer,
    UserImageSerializer,
)
from post.serializers import PostSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthorOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "upload_image":
            return UserImageSerializer
        return self.serializer_class

    def get_queryset(self):
        email = self.request.query_params.get("email")
        queryset = self.queryset

        if email:
            queryset = queryset.filter(email__icontains=email)

        return queryset

    @action(detail=True, methods=["POST"], url_path="upload-image", permission_classes=[IsAuthenticated])
    def upload_image(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="follow-unfollow", permission_classes=[IsAuthenticated])
    def follow_unfollow(self, request, pk=None):
        following = self.get_object()
        follower = self.request.user
        if following in follower.followings.all():
            follower.followings.remove(following)
            following.followers.remove(follower)
            return Response(status=status.HTTP_200_OK)
        follower.followings.add(following)
        following.followers.add(follower)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="followers", permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        user = User.objects.get(pk=pk)
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="following", permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        user = User.objects.get(pk=pk)
        following = user.followings.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="posts", permission_classes=[IsAuthenticated])
    def posts(self, request, pk=None):
        user = User.objects.get(pk=pk)
        posts = user.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="liked-posts", permission_classes=[IsAuthenticated])
    def liked_posts(self, request, pk=None):
        user = User.objects.get(pk=pk)
        likes = user.post_like.all()
        serializer = PostSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
