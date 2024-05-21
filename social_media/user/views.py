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
from .models import User, Hashtag, Post, Comment

from .serializers import (
    UserSerializer,
    UserListSerializer,
    UserImageSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentSerializer,
    HashtagSerializer,
    HashtagListSerializer,
    HashtagDetailSerializer,
)


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


class HashtagViewSet(generics.ListCreateAPIView,
                     mixins.UpdateModelMixin,
                     generics.RetrieveAPIView,
                     viewsets.GenericViewSet):
    serializer_class = HashtagSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Hashtag.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return HashtagListSerializer
        if self.action == "retrieve":
            return HashtagDetailSerializer
        return self.serializer_class


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrIfAuthenticatedReadOnly]
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "upload_image":
            return PostImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        user_following = user.followings.all()
        queryset = self.queryset.filter(
            Q(author=user) | Q(author__in=user_following)
        )

        hashtags = self.request.query_params.get("hashtags")
        author_email = self.request.query_params.get("author_last_name")
        if hashtags:
            queryset = queryset.filter(hashtags__name__icontains=hashtags)

        if author_email:
            queryset = queryset.filter(author__email__icontains=author_email)

        return queryset

    @action(detail=True, methods=["POST"], url_path="like-unlike", permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(post)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            post.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        post.likes.add(request.user)
        post.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="upload-image", permission_classes=[IsAuthenticated])
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = PostImageSerializer(post, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthorOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        if self.action in ["retrieve", "list"]:
            post_id = self.request.query_params.get("post_id")
            queryset = queryset.filter(post__id=post_id)

            return queryset
        return queryset

    def perform_create(self, serializer):
        post_id = self.request.query_params.get("post_id")
        serializer.save(author=self.request.user, post=Post.objects.get(id=post_id))
