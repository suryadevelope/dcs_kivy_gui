from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy_garden.mapview import MapView
from kivy_garden.mapview import MapMarker, MapView
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy_garden.mapview.utils import get_zoom_for_radius, haversine

import cv2
import webbrowser

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)  # Initialize OpenCV camera
        # Initialize map source
        source = "http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

        options = {}
        layer = GeoJsonMapLayer(source=source)

        if layer.geojson:
            # try to auto center the map on the source
            lon, lat = layer.center
            options["lon"] = lon
            options["lat"] = lat
            min_lon, max_lon, min_lat, max_lat = layer.bounds
            radius = haversine(min_lon, min_lat, max_lon, max_lat)
            zoom = get_zoom_for_radius(radius, lat)
            options["zoom"] = zoom

        view = MapView(**options)
        view.add_layer(layer)
        self.ids.mapview_con.add_widget(view)

        Clock.schedule_interval(self.update_camera, 1.0 / 30)  # Update the feed at 30 FPS

    def update_camera(self, dt):
        ret, frame = self.capture.read()  # Read a frame from the camera
        if ret:
            # Convert the image from BGR (OpenCV format) to RGB (Kivy format)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Get the image dimensions
            buf = frame.tobytes()  # Convert the image to bytes
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            # Display the texture in the `Image` widget
            self.ids.top_camera_feed.texture = texture

    def open_url(self, url):
        """Open the given URL in the web browser."""
        webbrowser.open(url)

    def set_map_location(self, lat, lon, zoom=10):
        """Set the map location and zoom level."""
        self.ids.mapview.lat = lat
        self.ids.mapview.lon = lon
        self.ids.mapview.zoom = zoom

    def on_stop(self):
        # Release the camera when closing the app
        self.capture.release()
