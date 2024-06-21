from rest_framework import serializers


class ContactUsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()
