import asyncio
import cv2 as cv

from channels.generic.websocket import AsyncWebsocketConsumer


class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Start generating frames and streaming to the client
        async for frame_data in self.generate_frames():
            await self.send(bytes_data=frame_data)

    async def disconnect(self, close_code):
        pass

    async def generate_frames(self):
        camera = cv.VideoCapture(
            0
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
