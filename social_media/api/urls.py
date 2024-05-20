from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, CommentViewSet

app_name = "api"

router = routers.DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [path("", include(router.urls))]
