from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy_garden.mapview import MapView
from kivy_garden.mapview import MapMarker, MapView,MapSource
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy_garden.mapview.utils import get_zoom_for_radius, haversine

import cv2

class MainScreen(Screen):
    grid_layout = ObjectProperty()

    def add_items(self):
        self.capture = cv2.VideoCapture(0)  # Initialize OpenCV camera
        # Initialize map source
        # ['osm', 'osm-hot', 'osm-de', 'osm-fr', 'cyclemap', 'thunderforest-cycle', 'thunderforest-transport', 'thunderforest-landscape', 'thunderforest-outdoors'])
        source = "http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        print(MapSource.providers.keys())

        options = {}
        layer = GeoJsonMapLayer(source=source)

        # if layer.geojson:
        # try to auto center the map on the source
        lon, lat = layer.center
        options["lon"] = lon
        options["lat"] = lat
        # min_lon, max_lon, min_lat, max_lat = layer.bounds
        # radius = haversine(min_lon, min_lat, max_lon, max_lat)
        # zoom = get_zoom_for_radius(radius, lat)
        # options["zoom"] = zoom
        # options["map_source"]=MapView.map_source('MyCustomTiles', url=source, subdomains=['mt0','mt1','mt2','mt3'])
        

        # view = MapView(**options)
        # view.MapSource(source=source, subdomains=['mt0','mt1','mt2','mt3'])
        # view.add_layer(layer)
        # self.ids.mapview_con.add_widget(view)

        Clock.schedule_interval(self.update_camera, 1.0 / 30)

        # Dynamically add buttons to the grid
        self.ids.box.add_widget(
                MDTopAppBar(
                    type_height="small",
                    headline_text=f"Headline {'small'.lower()}",
                    md_bg_color="#2d2734",
                    left_action_items=[["arrow-left", lambda x: x]],
                    right_action_items=[
                        ["attachment", lambda x: x],
                        ["calendar", lambda x: x],
                        ["dots-vertical", lambda x: x],
                    ],
                    title="Title"
                )
            )
    def update_camera(self, dt):
        ret, frame = self.capture.read()  # Read a frame from the camera
        if ret:
            # Convert the image from BGR (OpenCV format) to RGB (Kivy format)
            frame = cv2.flip(frame, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Get the image dimensions
            buf = frame.tobytes()  # Convert the image to bytes
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            # Display the texture in the `Image` widget
            self.ids.camera_feed.texture = texture

    def set_map_location(self, lat, lon, zoom=10):
        """Set the map location and zoom level."""
        self.ids.mapview.lat = lat
        self.ids.mapview.lon = lon
        self.ids.mapview.zoom = zoom

    def on_stop(self):
        # Release the camera when closing the app
        self.capture.release()

class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("./test1.kv")

    def on_start(self):
        # Add initial items dynamically
        self.root.get_screen("main").add_items()

# Create and run the app
MyApp().run()
