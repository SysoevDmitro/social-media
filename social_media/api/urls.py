from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, CommentViewSet, UserProfileViewSet

app_name = "api"

router = routers.DefaultRouter()
router.register(r"profiles", UserProfileViewSet, basename="profiles")
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [path("", include(router.urls))]
