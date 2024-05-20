from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .serializers import UserSerializer

User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserSearchAPIView(APIView):
    def get(self, request):
        query_params = request.query_params
        search_query = query_params.get("q", None)  # Get the search query from query parameters

        if search_query:
            # Perform the search query on User model
            users = User.objects.filter(username__icontains=search_query)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Please provide a search query."}, status=400)
