import random
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy_garden.mapview import MapMarkerPopup, MapView,MapSource
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty
from kivymd.uix.toolbar import MDTopAppBar
from kivy.graphics import Rotate, PushMatrix, PopMatrix
import cv2
from utils.audiosetting import text_sound
from utils.face_identify import facedetection
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Translate, Ellipse
from kivy.storage.jsonstore import JsonStore

from utils.nav_map_util import nav_util
from utils.speed_meter import Speedometer
from utils.fuel_meter import Fuel_meter




class CameraWidget(Image):
    def __init__(self, camera_index,image,camtype, **kwargs):
        super().__init__(**kwargs)
        self.camera_index = camera_index
        self.capture = cv2.VideoCapture(camera_index)
        self.is_running = True
        self.image = image
        self.camtype="face"
        self.facedetect=facedetection()
        self.audio=text_sound()
        self.drivername = None
        self.isfrontcamopened=False
        self.start_camera()

    def start_camera(self):
        def update(_):
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    
                    frame = cv2.flip(frame, 0)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    if self.camtype == "face":
                        # print("face cam")
                        # Convert the image from BGR (OpenCV format) to RGB (Kivy format)
                        facedata = self.facedetect.start_detect(frame)
                        if("status" not in facedata[0]):
                            frame = facedata[1]
                            if(len(facedata[0]["person"])>0 and self.drivername == None):
                                self.audio.play("Hi "+str(facedata[0]["person"])+", facial authentication successful")
                                self.drivername = str(facedata[0]["person"])
                                
                            
                        else:
                            print(facedata[0])

                    elif(self.camtype == "front"):
                        print("front cam")

                    # Get the image dimensions
                    # if self.drivername == None:
                    buf = frame.tobytes()  # Convert the image to bytes
                    texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                    texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                    # Display the texture in the `Image` widget
                    self.image.texture = texture

        # Schedule updates on the main thread
        Clock.schedule_interval(update, 1.0 / 30)  # 30 FPS

    def stop_camera(self):
        self.is_running = False
        self.capture.release()


class HomeScreen(Screen):
    grid_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog=None
        self.add_items()
        self.facedetect=facedetection()
        self.audio=text_sound()
        self.drivername = None
        
    def add_items(self):
        self.capture = CameraWidget(camera_index=0,image=self.ids.camera_feed,camtype="face")  # Initialize OpenCV camera
        self.frontcapture = CameraWidget(camera_index=2,image=self.ids.camera_feed,camtype="front")  # Initialize OpenCV camera
        # Initialize map source
        # ['osm', 'osm-hot', 'osm-de', 'osm-fr', 'cyclemap', 'thunderforest-cycle', 'thunderforest-transport', 'thunderforest-landscape', 'thunderforest-outdoors'])
        satellite_map_source = MapSource(
            url="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            min_zoom=10,
            max_zoom=19,
            tile_size=256,            
        )

        self.ids.main_map_me.lat = 17.41256
        self.ids.main_map_me.lon = 78.52648

        self.ids.main_map.map_source = satellite_map_source
        self.ids.main_map.zoom = 15
        self.ids.main_map.center_on(self.ids.main_map_me.lat, self.ids.main_map_me.lon)

        # Set up the MapView with the custom tile source
        # self.mapview = MapView(
        #     lat=17.56565,  # Latitude
        #     lon=78.25648,  # Longitude
        #     zoom=1,  # Initial zoom level
        #     map_source=satellite_map_source
        # )

        # Marker for current location
       

        self.ids.main_map.bind(on_touch_down=self.open_map_dialog)

        self.store = JsonStore("nav_map.json")
        if(self.store.exists("data")):
            self.latlngdata = self.store['data']['data']
        
        if(len(self.latlngdata)>0):

            navutil = nav_util(self.ids.main_map)
            self.ids.main_map.lat=self.latlngdata[0]
            self.ids.main_map.lon=self.latlngdata[1]
            self.ids.main_map.zoom = 16
            # navutil.press_dist(res1=self.latlngdata)

            print(self.latlngdata)
            
        
       
        # self.ids.mapview_con.add_widget(self.mapview)

        # Clock.schedule_interval(self.update_camera, 1.0 / 30)
        # Clock.schedule_interval(self.update_front_camera, 1.5 / 30)
        

        # Dynamically add buttons to the grid
        self.ids.box.add_widget(
                MDTopAppBar(
                    type_height="small",
                    headline_text=f"Headline {'small'.lower()}",
                    md_bg_color="#2d2734",
                    # left_action_items=[["arrow-left", lambda x: x]],
                    right_action_items=[
                        ["attachment", lambda x: x],
                        ["calendar", lambda x: x],
                        ["dots-vertical", lambda x: x],
                    ],
                    title="Title"
                )
            )
    def press(self, instance):
        print("Main marker pressed")

    def update_marker_position(self, lat, lon, angle):
        """Updates the marker's position and rotation."""
        self.main_map_me.lat = lat
        self.main_map_me.lon = lon
        self.marker_rotation.angle = angle
        self.main_map_me.canvas.ask_update() 
        print(f"Marker updated to lat: {lat}, lon: {lon}, angle: {angle}")

    def update_front_camera(self, dt):
        if self.drivername != None:
            ret, ftframe = self.frontcapture.read()  # Read a frame from the camera
            if ret:
                ftframe = cv2.flip(ftframe, 0)
                buf = ftframe.tobytes()  # Convert the image to bytes
                texture = Texture.create(size=(ftframe.shape[1], ftframe.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                # Display the texture in the `Image` widget
                self.ids.camera_feed.texture = texture

    def update_camera(self, dt):
        # self.update_marker_position(17.56565,78.25648,random.randint(0, 360))
        ret, frame = self.capture.read()  # Read a frame from the camera
        if ret:
            # Convert the image from BGR (OpenCV format) to RGB (Kivy format)
            frame = cv2.flip(frame, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            facedata = self.facedetect.start_detect(frame)
            if("status" not in facedata[0]):
                frame = facedata[1]
                if(len(facedata[0]["person"])>0 and self.drivername == None):
                    self.audio.play("Hi "+str(facedata[0]["person"])+", facial authentication successful")
                    self.drivername = str(facedata[0]["person"])
                
            else:
                print(facedata[0])

            

            # Get the image dimensions
            if self.drivername == None:
                buf = frame.tobytes()  # Convert the image to bytes
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                # Display the texture in the `Image` widget
                self.ids.camera_feed.texture = texture

  
    def updatefullscreen(self, main_image_widget, popup_image_widget):
        """Update the fullscreen popup image texture."""
        popup_image_widget.texture = main_image_widget.texture

    
    def open_map_dialog(self,dt,touch):
        """Open a full-screen popup dialog."""
        if self.ids.main_map.collide_point(*touch.pos):
            # popup_layout = BoxLayout(orientation='vertical')
            # satellite_map_source = MapSource(
            #     url="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            #     min_zoom=1,
            #     max_zoom=19,
            #     tile_size=256,            
            # )

            # # Set up the MapView with the custom tile source
            # mapview = MapView(
            #     lat=10.4862,  # Latitude
            #     lon=10.5924,  # Longitude
            #     zoom=18,  # Initial zoom level
            #     map_source=satellite_map_source
            # )
         
            # # Marker for current location
            # self.main_map_me = MapMarkerPopup(lat=17.464484, lon=78.593891, source='assets/nav_icon.png')
            # self.icon_size = (50, 50)  # Icon dimensions

            # with self.main_map_me.canvas.before:
            #     PushMatrix()
            #     self.marker_rotation = Rotate(angle=0, origin=(self.icon_size[0] / 2, self.icon_size[1] / 2))
            #     Ellipse(source='../assets/nav_icon.png', size=self.icon_size, pos=(0, 0))
            #     PopMatrix()
            
            

            # mapview.add_widget(self.main_map_me)
            # close_btn = Button(text='Close', size_hint=(1, 0.1))

            # popup_layout.add_widget(mapview)
            # popup_layout.add_widget(close_btn)

            # popup = ModalView( auto_dismiss=False, size_hint=(1, 1))  # Full screen
            # popup.add_widget(popup_layout)
            # # Bind the close button to dismiss the popup
            # close_btn.bind(on_release=lambda instance: self.dismiss_mapfull_screen(popup))

            # # Open the popup
            # popup.open()
            self.store = JsonStore("nav_map.json")
            self.store.put("data", data=[])
            print("")
            self.manager.current="fullmap"
       
    def dismiss_mapfull_screen(self, popup):
        """Dismiss the full-screen popup and stop updates."""
        popup.dismiss()

    
    def open_dialog(self, main_image_widget):
        """Open a full-screen popup dialog."""
        
        self.update_full_screen_val = True
        popup_layout = BoxLayout(orientation='vertical')
        popup_image = Image(size_hint=(1, 1), allow_stretch=True, keep_ratio=False)
        close_btn = Button(text='Close', size_hint=(1, 0.1))

        popup_layout.add_widget(popup_image)
        popup_layout.add_widget(close_btn)

        popup = Popup(content=popup_layout, auto_dismiss=False, size_hint=(1, 1))
       
        # Bind the close button
        close_btn.bind(on_release=lambda instance: self.dismiss_full_screen(popup))

        # Open the popup
        popup.open()

        # Start updating the popup image
        Clock.schedule_interval(lambda dt: self.updatefullscreen(main_image_widget, popup_image), 1.0 / 30.0)

    def dismiss_full_screen(self, popup):
        """Dismiss the full-screen popup and stop updates."""
        Clock.unschedule(self.updatefullscreen)  # Stop updating the popup image
        popup.dismiss()

    def on_stop(self):
        # Release the camera when closing the app
        self.capture.release()
        self.frontcapture.release()

    def change_screen(self, screen_name):
        # Change the screen dynamically based on button press
        print(screen_name)
        self.manager.current = "allapps"
    