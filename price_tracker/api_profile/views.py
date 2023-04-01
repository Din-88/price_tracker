from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView

from .serializers import UserSerializer


class AccountBasics(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    http_method_names = ['get', "post", "put", "patch", ]

    def get_object(self):
        return self.request.user
