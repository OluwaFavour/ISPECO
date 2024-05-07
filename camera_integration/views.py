from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import AddCameraSerializer, CameraSerializer
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


class CameraView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            camera = Camera.objects.get(id=kwargs["id"])
        except Camera.DoesNotExist:
            return Response(
                {"message": "Camera not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CameraSerializer(camera)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if kwargs:
            return Response(
                {"message": "Invalid URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AddCameraSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            camera = serializer.save()
            response_serializer = CameraSerializer(camera)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            camera = Camera.objects.get(id=kwargs["id"])
        except Camera.DoesNotExist:
            return Response(
                {"message": "Camera not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AddCameraSerializer(camera, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = CameraSerializer(camera)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        try:
            camera = Camera.objects.get(id=kwargs["id"])
        except Camera.DoesNotExist:
            return Response(
                {"message": "Camera not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AddCameraSerializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = CameraSerializer(camera)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            camera = Camera.objects.get(id=kwargs["id"])
        except Camera.DoesNotExist:
            return Response(
                {"message": "Camera not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCameraView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CameraSerializer

    def get_queryset(self):
        return Camera.objects.filter(user=self.request.user)


class CameraDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CameraSerializer

    def get_queryset(self):
        return Camera.objects.filter(user=self.request.user)


class CameraPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            camera = Camera.objects.get(id=kwargs["id"])
        except Camera.DoesNotExist:
            return Response(
                {"message": "Camera not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if camera.user != request.user:
            return Response(
                {"message": "This user does not have access to this camera"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"password": camera.password})
