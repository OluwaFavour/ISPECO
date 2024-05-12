from drf_spectacular.utils import extend_schema, inline_serializer
from knox.auth import TokenAuthentication
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response

from .serializers import CameraInSerializer, CameraOutSerializer
from .models import Camera


class CameraCreateView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = CameraInSerializer

    @extend_schema(
        request=CameraInSerializer,
        responses={
            201: CameraOutSerializer(many=False),
        },
        description="Create a new camera.",
    )
    def post(self, request, *args, **kwargs):
        serializer = CameraInSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CameraView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = CameraInSerializer

    @extend_schema(
        responses={
            200: CameraOutSerializer(many=False),
            403: inline_serializer(
                name="CameraGet",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="CameraGetError",
                fields={"message": serializers.CharField()},
            ),
        },
        description="Get details of a specific camera by ID specified in the URL",
    )
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
        serializer = self.get_serializer(camera)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CameraInSerializer,
        responses={
            200: CameraOutSerializer(many=False),
            403: inline_serializer(
                name="CameraPatch",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="CameraPatchError",
                fields={"message": serializers.CharField()},
            ),
        },
        description="partially update details of a camera specified by ID in the URL.",
    )
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
        serializer = self.get_serializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: None,
            403: inline_serializer(
                name="CameraDel",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="CameraDelError",
                fields={"message": serializers.CharField()},
            ),
        },
        description="Delete a camera specified by ID in the URL.",
    )
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
    serializer_class = CameraOutSerializer

    @extend_schema(
        responses={
            200: CameraOutSerializer(many=True),
        },
        description="Retrieve a list of cameras owned by the authenticated user.",
    )
    def get_queryset(self):
        return Camera.objects.filter(user=self.request.user)


class CameraPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={
            200: inline_serializer(
                name="Password200",
                fields={"password": serializers.CharField()},
            ),
            403: inline_serializer(
                name="Password403",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="Password404",
                fields={"message": serializers.CharField()},
            ),
        },
        description="Retrieve the password of a camera specified by ID in the URL.",
    )
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
        return Response({"password": camera.password}, status=status.HTTP_200_OK)


class CameraUrlView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses={
            200: inline_serializer(
                name="Url200",
                fields={"url": serializers.CharField()},
            ),
            403: inline_serializer(
                name="Url403",
                fields={"message": serializers.CharField()},
            ),
            404: inline_serializer(
                name="Url404",
                fields={"message": serializers.CharField()},
            ),
        },
        description="Retrieve the URL of a camera specified by ID in the URL.",
    )
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
        return Response({"url": camera.url}, status=status.HTTP_200_OK)
