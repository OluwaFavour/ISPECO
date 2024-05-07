from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import AddCameraSerializer
from .models import Camera


class AddCameraView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddCameraSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            camera = serializer.save()
            return Response(
                {"id": camera.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCameraView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        camera = Camera.objects.get(id=kwargs["id"])
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
