import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.graphics import Rectangle, Color, Line, Bezier, Ellipse, Triangle, Rotate
from functools import partial
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker, MapSource
import requests
import re
from kivy.storage.jsonstore import JsonStore


class Fullmapscreen(Screen):
    my_avat = StringProperty()
    rotation_angle = NumericProperty(0)  # Rotation angle for the user location image

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_of_lines = []
        self.route_points = []
        self.placed = False
        self.exists = False
        self.res1 = None

        # Set up satellite map source
        satellite_source = MapSource(
            url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",  # URL for Google Satellite Tiles
            attribution="Google Satellite",  # Attribution text
            max_zoom=19,  # Maximum zoom level
            min_zoom=0,   # Minimum zoom level
            tile_size=256,  # Tile size in pixels
            image_ext="png"  # Image extension
        )

        # Configure map
        self.ids.main_map.map_source = satellite_source
        self.ids.main_map.zoom = 15
        self.ids.main_map.center_on(self.ids.main_map_me.lat, self.ids.main_map_me.lon)
        self.my_avat = 'avatar.png'

        # Schedule the rotation of the avatar image (user location icon)
        Clock.schedule_interval(self.rotate_user_location, 0.1)  # Rotate every 0.1 seconds
        self.place_pin()
    
    def change_screen(self,screen):
        if(self.res1):
            self.store = JsonStore("nav_map.json")
            self.store.put("data", data=self.res1)

        
        self.manager.current = screen

    def rotate_user_location(self, dt):
        """Rotate the user location image by 1 degree every interval."""
        self.rotation_angle += 1  # Increment the angle by 1 degree
        if self.rotation_angle >= 360:  # Reset after a full rotation
            self.rotation_angle = 0

        # Apply the rotation to the user location image
        if self.exists:
            # Rotate the user location image (MapMarkerPopup or custom Image widget)
            self.dist.rotation = self.rotation_angle

    def press(self):
        print(str(self.ids.main_map_me.lat) + ' | ' + str(self.ids.main_map_me.lon))

    def place_pin(self):
        self.placed = True
        

    def remove_pin(self):
        if self.exists:
            self.ids.main_map.remove_widget(self.dist)
            self.clear_route()
            self.placed = False
            self.exists = False

    def clear_route(self):
        # Remove all route points and lines
        for point in self.route_points:
            self.ids.main_map.remove_widget(point)
        self.route_points.clear()

        for line in self.list_of_lines:
            self.canvas.remove(line)
        self.list_of_lines.clear()

    def on_touch_up(self, touch):
        print("map on touch")
        if touch.y > self.height * 0.05:
            if self.placed and not self.exists:
                # self.remove_pin()
                self.dist = MapMarkerPopup(lat=self.ids.main_map.get_latlon_at(touch.x, touch.y)[0],
                                           lon=self.ids.main_map.get_latlon_at(touch.x, touch.y)[1],
                                           source='assets/dliverypoint.png')

                # Rotate user location image and add button to print location
                self.btn = Button(text='print loc', on_press=self.press_dist)
                self.dist.add_widget(self.btn)
                self.ids.main_map.add_widget(self.dist)
                print(self.ids.main_map.get_latlon_at(touch.x, touch.y))
                self.exists = True

    def press_dist(self, instance):
        # Clear previous route before drawing a new one
        self.clear_route()

        print(self.dist.lat)
        print(self.dist.lon)

        self.start_lon = self.ids.main_map_me.lon
        self.start_lat = self.ids.main_map_me.lat

        self.end_lon = self.dist.lon
        self.end_lat = self.dist.lat
        self.body = {"coordinates": [[self.start_lon, self.start_lat], [self.end_lon, self.end_lat]]}
        self.headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': '5b3ce3597851110001cf6248e32f3f787ba541e8b3d916f4681b9340',
            'Content-Type': 'application/json; charset=utf-8'}
        self.call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/gpx', json=self.body, headers=self.headers)
        print(self.call.text)
        self.string_res = self.call.text

        print(self.string_res)

        self.tag = 'rtept'
        self.reg_str = '</' + self.tag + '>(.*?)' + '>'  # find the route point tags
        self.res = re.findall(self.reg_str, self.string_res)
        print(self.res)
        print('_____________________________________')
        self.string1 = str(self.res)
        self.tag1 = '"'
        self.reg_str1 = '"' + '(.*?)' + '"'
        self.res1 = re.findall(self.reg_str1, self.string1)
        print(self.res1)

        # Add route waypoints as MapMarkerPopups
        for i in range(0, len(self.res1) - 1, 2):
            print('lat= ' + self.res1[i])
            print('lon= ' + self.res1[i + 1])

            self.points_lat = float(self.res1[i])  # Convert to float for geographic accuracy
            self.points_lon = float(self.res1[i + 1])

            self.points_pop = MapMarkerPopup(lat=self.points_lat, lon=self.points_lon, source='waypoint.png')
            self.route_points.append(self.points_pop)

            self.ids.main_map.add_widget(self.points_pop)

        # Draw lines connecting the waypoints
        with self.canvas:
            Color(0.5, 0, 0, 1)
            for j in range(0, len(self.route_points) - 1, 1):
                self.lines = Line(points=(self.route_points[j].pos[0], self.route_points[j].pos[1],
                                          self.route_points[j + 1].pos[0], self.route_points[j + 1].pos[1]), width=4)
                self.list_of_lines.append(self.lines)

        # Update waypoints position on map move or zoom
        Clock.schedule_interval(self.update_route_lines, 1 / 1000)

    def update_route_lines(self, *args):
        for j in range(1, len(self.route_points), 1):
            self.list_of_lines[j - 1].points = [self.route_points[j - 1].pos[0], self.route_points[j - 1].pos[1],
                                                self.route_points[j].pos[0], self.route_points[j].pos[1]]


