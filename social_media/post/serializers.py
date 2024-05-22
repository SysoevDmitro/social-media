from rest_framework import serializers
from .models import Hashtag, Post, Comment
from user.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")
        read_only_fields = ("created_at",)


class HashtagField(serializers.CharField):
    def to_representation(self, value):
        if value:
            return f"#{value}"
        return None

    def to_internal_value(self, data):
        hashtag_value = data.lstrip("#")
        return super().to_internal_value(hashtag_value)


class HashtagSerializer(serializers.ModelSerializer):
    name = HashtagField(required=False)

    class Meta:
        model = Hashtag
        fields = ("id", "name")


class HashtagListSerializer(HashtagSerializer):
    posts = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model = Hashtag
        fields = ("id", "name", "posts")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    hashtags = HashtagSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "content",
                  "images",
                  "comments",
                  "created_at",
                  "hashtags",
                  )

    def create(self, validated_data):
        hashtags = validated_data.pop("hashtags", None)
        post = Post.objects.create(**validated_data)

        if hashtags:
            for hashtag in hashtags:
                hashtag_name, _ = Hashtag.objects.get_or_create(name=hashtag["name"])
                post.hashtags.add(hashtag_name)

        return post

    def update(self, instance, validated_data):
        hashtags = validated_data.pop("hashtags", None)
        instance = super().update(instance, validated_data)

        if hashtags:
            for hashtag in hashtags:
                hashtag_name, _ = Hashtag.objects.get_or_create(name=hashtag["name"])
                instance.hashtags.add(hashtag_name)

        return instance


class PostListSerializer(PostSerializer):
    author = serializers.SlugRelatedField(slug_field="email", read_only=True)
    hashtags = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    likes = serializers.IntegerField(read_only=True, source="likes.count")
    comments = serializers.IntegerField(read_only=True, source="comments.count")

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "likes",
                  "comments",
                  "hashtags",
                  "images")


class PostDetailSerializer(PostSerializer):
    author = UserSerializer(read_only=True)
    hashtags = HashtagSerializer(read_only=True)
    comments = CommentSerializer(read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Post
        fields = ("id",
                  "author",
                  "content",
                  "images",
                  "likes",
                  "comments",
                  "created_at")


class HashtagDetailSerializer(HashtagSerializer):
    posts = PostListSerializer(read_only=True, many=True)

    class Meta:
        model = Hashtag
        fields = ("id", "name", "posts")
