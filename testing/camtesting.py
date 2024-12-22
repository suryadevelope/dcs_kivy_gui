import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class CameraWidget(Image):
    def __init__(self, camera_index, **kwargs):
        super().__init__(**kwargs)
        self.camera_index = camera_index
        self.capture = cv2.VideoCapture(camera_index)
        self.is_running = True
        self.start_camera()

    def start_camera(self):
        def update(_):
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    # Flip the frame horizontally to correct the mirrored view
                    frame = cv2.flip(frame, 1)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    buffer = frame.tobytes()
                    texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                    texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
                    self.texture = texture

        # Schedule updates on the main thread
        Clock.schedule_interval(update, 1.0 / 30)  # 30 FPS

    def stop_camera(self):
        self.is_running = False
        self.capture.release()


class DualCameraApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical")

        # Create two camera widgets
        self.camera1 = CameraWidget(camera_index=0)
        self.camera2 = CameraWidget(camera_index=2)

        layout.add_widget(self.camera1)
        layout.add_widget(self.camera2)

        return layout

    def on_stop(self):
        # Stop cameras when the app is closed
        self.camera1.stop_camera()
        self.camera2.stop_camera()


if __name__ == "__main__":
    DualCameraApp().run()
