from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

from server.auth_request import authenticate_device

class SplashScreen(Screen):
    def on_enter(self):
        # Schedule transition to LoginScreen after 5 seconds
        self.store = JsonStore("auth_info.json")

        device_token = authenticate_device("80:00:00:00:00:01")

        # Check if authentication was successful and token was received
        if device_token and "dcs_token" in device_token:
            # Save the device token in local storage
            self.store.put("devicetoken", token=device_token["dcs_token"])
            print("Device token received and stored.",device_token)
        
        Clock.schedule_once(self.switch_to_login, 3)

    def switch_to_login(self, *args):

        if self.store.exists("auth_token"):
            self.manager.current = "home"  # Navigate to home screen
        else:
            self.manager.current = "home"  # Navigate to login screen
