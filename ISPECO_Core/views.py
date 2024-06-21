from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ISPECO_Core.serializers import ContactUsSerializer


class HealthCheckView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({"message": "Healthy"}, status=status.HTTP_200_OK)


class ContactUsView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ContactUsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        message = serializer.validated_data["message"]
        try:
            send_mail(
                subject=f"Contact Us Message from {email}",
                message=message,
                from_email=email,
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"message": "Failed to send message"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "Message Sent"}, status=status.HTTP_200_OK)
