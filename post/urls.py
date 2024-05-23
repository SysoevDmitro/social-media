from django.urls import include, path
from rest_framework import routers

from .views import CommentViewSet, PostViewSet, HashtagViewSet

router = routers.DefaultRouter()
router.register(r"Comment", CommentViewSet, basename="comment")
router.register(r"Post", PostViewSet, basename="post")
router.register(r"Hashtag", HashtagViewSet, basename="Hashtag")

comment_list = CommentViewSet.as_view(
    actions={"get": "list", "post": "create"})


urlpatterns = [path("posts/<int:pk>/comments/", comment_list, name="comment-post")] + router.urls

app_name = "post"
