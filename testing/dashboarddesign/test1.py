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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout

import cv2
from testing.dashboarddesign.appsview import Appsview

class MainScreen(Screen):
    def __init__(self, **kw):
        self.dialog=None
        self.alliconsview = Appsview()

        super().__init__(**kw)

    grid_layout = ObjectProperty()

    def add_items(self):
        self.capture = cv2.VideoCapture(0)  # Initialize OpenCV camera
        # Initialize map source
        # ['osm', 'osm-hot', 'osm-de', 'osm-fr', 'cyclemap', 'thunderforest-cycle', 'thunderforest-transport', 'thunderforest-landscape', 'thunderforest-outdoors'])
        satellite_map_source = MapSource(
            url="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
           
            min_zoom=1,
            max_zoom=19,
            tile_size=256,
        )

        # Set up the MapView with the custom tile source
        mapview = MapView(
            lat=0,  # Latitude
            lon=0,  # Longitude
            zoom=2,  # Initial zoom level
            map_source=satellite_map_source
        )
        self.ids.mapview_con.add_widget(mapview)

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
    
    def show_popup(self,type):
        print(type)

        content_final=MDBoxLayout(
                orientation="vertical",
                spacing="12dp",
                adaptive_height=True,
                children=[
                    MDRaisedButton(
                        text="Option 1",
                        size_hint=(None, None),
                        size=("200dp", "48dp"),
                        on_release=lambda x: self.close_popup()
                    ),
                    MDRaisedButton(
                        text="Option 2",
                        size_hint=(None, None),
                        size=("200dp", "48dp"),
                        on_release=lambda x: self.close_popup()
                    ),
                ]
            )
        if(type=="apps"):
            content_final=self.ids.appswindow
            self.alliconsview.update_grid(content_final)
            
        

        if not self.dialog:
            self.dialog = MDDialog(
                title="Popup Window",
                type="custom",
                content_cls=content_final,
                buttons=[
                    MDRaisedButton(
                        text="CLOSE",
                        on_release=lambda x: self.close_popup()
                    ),
                ],
            )
        self.dialog.open()

    def close_popup(self):
        if self.dialog:
            self.dialog.dismiss()

    def on_stop(self):
        # Release the camera when closing the app
        self.capture.release()
    

class MyApp(MDApp):
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("./allapps.kv")
        return Builder.load_file("./test1.kv")

    def on_start(self):
        
        # Add initial items dynamically
        self.root.get_screen("main").add_items()

# Create and run the app
MyApp().run()
