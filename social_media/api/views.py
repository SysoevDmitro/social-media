from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Post, Comment
from .serializers import PostSerializer, PostListSerializer, CommentSerializer, PostDetailSerializer
from .permissions import IsOwnerOrReadOnly
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
