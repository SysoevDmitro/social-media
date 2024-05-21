from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet, CommentViewSet, PostViewSet, HashtagViewSet, CreateUserView


comment_list = CommentViewSet.as_view(
    actions={"get": "list", "post": "create"}
)
router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("comments", CommentViewSet)
router.register("posts", PostViewSet)
router.register("hashtags", HashtagViewSet)

urlpatterns = [path("users/register/", CreateUserView.as_view(), name="user-create"),
               path("users/login/", TokenObtainPairView.as_view(), name="user-obtain-pair"),
               path("users/login/refresh/", TokenRefreshView.as_view(), name="user-refresh"),
               path("users/login/verify/", TokenVerifyView.as_view(), name="user-verify"),
               path("posts/<int:pk>/comments/", comment_list, name="comment-post")
               ] + router.urls


app_name = "user"
