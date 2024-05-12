import asyncio
import cv2 as cv

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from camera_integration.models import Camera


@database_sync_to_async
def get_camera_user(cam_id: int):
    """
    Retrieves the user associated with a given camera ID.

    Args:
        cam_id (int): The ID of the camera.

    Returns:
        User: The user associated with the camera.

    Raises:
        Camera.DoesNotExist: If the camera with the given ID does not exist.
    """
    return Camera.objects.get(id=cam_id).user


@database_sync_to_async
def get_camera_url(cam_id: int):
    """
    Retrieves the URL of a camera based on its ID.

    Args:
        cam_id (int): The ID of the camera.

    Returns:
        str: The URL of the camera.

    Raises:
        Camera.DoesNotExist: If the camera with the given ID does not exist.
    """
    return Camera.objects.get(id=cam_id).url


class CameraConsumer(AsyncWebsocketConsumer):
    """
    Represents a consumer for streaming camera frames over a WebSocket connection.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.
        """
        self.user = self.scope["user"]
        self.cam_id = self.scope["url_route"]["kwargs"]["cam_id"]
        if self.user.is_anonymous:
            await self.close(code=4001, reason="Unauthorized")
        if self.user != await get_camera_user(self.cam_id):
            print("User does not have access to this camera...")
            await self.close(code=4001, reason="Unauthorized")
        self.cam_url = await get_camera_url(self.cam_id)
        await self.accept()

        # Start generating frames and streaming to the client
        async for frame_data in self.generate_frames():
            await self.send(bytes_data=frame_data)

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.
        """
        pass

    async def generate_frames(self):
        """
        Generates camera frames and yields them as bytes.
        """
        camera = cv.VideoCapture(
            self.cam_url if self.cam_url else 0
        )  # Use 0 for webcam, replace with camera URL for IP camera

        try:
            while True:
                success, frame = camera.read()
                if not success:
                    break

                # Convert frame to JPEG format
                ret, buffer = cv.imencode(".jpg", frame)
                if not ret:
                    continue

                # Convert frame buffer to bytes and yield
                yield buffer.tobytes()

                # Simulate processing delay
                await asyncio.sleep(0.1)  # Adjust delay as needed

        finally:
            camera.release()  # Release the camera capture
