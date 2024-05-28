from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response


class HealthCheckView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({"message": "Healthy"}, status=status.HTTP_200_OK)
