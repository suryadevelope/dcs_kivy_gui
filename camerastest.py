import threading
import cv2
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock

class DualCameraApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="horizontal")
        
        # Camera feed widgets
        self.cam1_image = Image(allow_stretch=True, keep_ratio=False)
        self.cam2_image = Image(allow_stretch=True, keep_ratio=False)
        
        self.layout.add_widget(self.cam1_image)
        self.layout.add_widget(self.cam2_image)
        
        # Initialize OpenCV video captures
        self.cam1 = cv2.VideoCapture(0, cv2.CAP_V4L2)  # DirectShow backend for Windows
        self.cam2 = cv2.VideoCapture(2, cv2.CAP_V4L2)  # DirectShow backend for Windows

        # Check if cameras are opened successfully
        if not self.cam1.isOpened():
            print("Camera 1 not available!")
        if not self.cam2.isOpened():
            print("Camera 2 not available!")

        # Set low resolution for reduced resource usage
        self.cam1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cam2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Start threads for independent camera frame capture
        self.thread1 = threading.Thread(target=self.capture_frames, args=(self.cam1, self.cam1_image))
        self.thread1.daemon = True
        self.thread1.start()

        self.thread2 = threading.Thread(target=self.capture_frames, args=(self.cam2, self.cam2_image))
        self.thread2.daemon = True
        self.thread2.start()

        return self.layout

    def capture_frames(self, camera, image_widget):
        while True:
            ret, frame = camera.read()
            if ret:
                # Convert frame to texture and update widget
                self.update_texture(image_widget, frame)

    def update_texture(self, widget, frame):
        """Convert OpenCV frame to Kivy texture and update the widget."""
        try:
            # Flip frame vertically (Kivy expects a flipped texture)
            buffer = cv2.flip(frame, 0).tobytes()
            # Create texture
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            texture.flip_vertical()
            # Update the widget's texture
            widget.texture = texture
        except Exception as e:
            print(f"Error updating texture: {e}")

    def on_stop(self):
        """Release resources when the app is stopped."""
        if self.cam1.isOpened():
            self.cam1.release()
        if self.cam2.isOpened():
            self.cam2.release()

if __name__ == "__main__":
    DualCameraApp().run()
