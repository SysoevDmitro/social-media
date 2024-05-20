from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.viewsets import GenericViewSet

from .models import Post, Comment
from .serializers import (PostListSerializer,
                          CommentSerializer,
                          PostDetailSerializer,
                          UserProfileListSerializer,
                          UserProfileDetailSerializer,
                          UserProfileSerializer,
                          UserProfilePictureSerializer,
                          UserFollowSerializer,)
from .permissions import IsOwnerUserOrReadOnly
from rest_framework.decorators import action


User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        post.likes.add(user)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get("content")
        comment = Comment.objects.create(author=request.user, post=post, content=content)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """User Profile"""

    queryset = (
        get_user_model()
        .objects.all()
        .annotate(
            followers_count=(Count("followers", distinct=True)),
            followed_by_count=(Count("followed_by", distinct=True)),
        )
    )
    permission_classes = [IsOwnerUserOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        if self.action == "retrieve":
            return UserProfileDetailSerializer
        if self.action == "set_picture":
            return UserProfilePictureSerializer
        if self.action in ("follow", "unfollow"):
            return UserFollowSerializer
        return UserProfileSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("followers")
        # filtering by email, first_name, last_name
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                Q(email__icontains=name)
                | Q(first_name__icontains=name)
                | Q(last_name__icontains=name)
            )
        return queryset

    @action(
        methods=["POST", "GET"],
        detail=True,
        url_path="picture",
        permission_classes=[IsOwnerUserOrReadOnly],
    )
    def set_picture(self, request, pk=None):
        """Endpoint for uploading user profile picture"""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Add current user to followers"""
        user_to_follow = self.get_object()
        user_to_follow.followers.add(self.request.user)
        return Response(
            {
                "detail": (
                    "Add follower: "
                    + self.request.user.email
                    + " to: "
                    + user_to_follow.email
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        """Delete current user from followers"""
        user_to_unfollow = self.get_object()
        user_to_unfollow.followers.remove(self.request.user)
        return Response(
            {
                "detail": (
                    "Delete follower: "
                    + self.request.user.email
                    + " from: "
                    + user_to_unfollow.email
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"],
        detail=True,
        url_path="followers",
        permission_classes=[IsAuthenticated],
    )
    def get_followers(self, request, pk=None):
        """List all followers"""
        user = self.get_object()
        serializer = UserFollowSerializer(user.followers.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="followed-by",
        permission_classes=[IsAuthenticated],
    )
    def get_followed_by(self, request, pk=None):
        """List all users that followed by current user"""
        user = self.get_object()
        followed_by = user.followed_by.all()
        serializer = UserFollowSerializer(followed_by, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by part of email or first_name "
                "or last_name (ex. ?name=value). "
                "Case-insensitive lookup that contains value",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
