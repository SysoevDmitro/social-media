from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",
                  "first_name",
                  "last_name",
                  "email",
                  "password",
                  "bio",
                  "followers",
                  "followings",
                  "profile_pic")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        return user


class UserListSerializer(UserSerializer):
    following = serializers.IntegerField(source="following.count", read_only=True)
    followers = serializers.IntegerField(source="followers.count", read_only=True)
    posts = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("id",
                  "username",
                  "email",
                  "first_name",
                  "last_name",
                  "profile_pic",
                  "following",
                  "followers",
                  "posts")


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "profile_pic")

