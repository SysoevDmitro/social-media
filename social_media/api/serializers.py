from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id",
                  "author",
                  "content",
                  "created_at",)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "content",
                  "media",
                  "created_at",)


class PostListSerializer(PostSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "content",
                  "media",
                  "created_at",
                  "likes_count",
                  "comments_count")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(PostListSerializer):
    author = serializers.SlugRelatedField(slug_field="email", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "content",
                  "media",
                  "created_at",
                  "likes_count",
                  "comments_count",
                  "comments")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "bio",
            "followers",
            "profile_picture",
        )
        read_only_fields = (
            "email",
            "full_name",
            "profile_picture",
        )


class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "full_name", "profile_picture")
        read_only_fields = (
            "email",
            "full_name",
        )


class UserProfileListSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    followed_by_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "followers_count",
            "followed_by_count",
            "profile_picture",
        )


class UserProfileDetailSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    followers = serializers.SlugRelatedField(
        slug_field="email", read_only=True, many=True
    )
    followed_by_count = serializers.IntegerField(read_only=True)
    followed_by = serializers.SlugRelatedField(
        slug_field="email", read_only=True, many=True
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "bio",
            "followers_count",
            "followers",
            "followed_by_count",
            "followed_by",
            "profile_picture",
        )


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "full_name",
            "profile_picture",
        )
        read_only_fields = (
            "email",
            "full_name",
            "profile_picture",
        )
