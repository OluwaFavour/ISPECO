from django.urls import re_path

from .consumers import CameraConsumer

websocket_urlpatterns = [
    re_path(r"ws/live_stream/(?P<cam_id>\d+)/$", CameraConsumer.as_asgi()),
]
