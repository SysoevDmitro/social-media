from django.db.models import Q
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Hashtag, Post, Comment
from .permissions import IsAuthorOrIfAuthenticatedReadOnly
from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentSerializer,
    HashtagSerializer,
    HashtagListSerializer,
    HashtagDetailSerializer,
)


class HashtagViewSet(mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
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
