from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

class SplashScreen(Screen):
    def on_enter(self):
        # Schedule transition to LoginScreen after 5 seconds
        Clock.schedule_once(self.switch_to_login, 5)

    def switch_to_login(self, *args):
        self.manager.current = "login"
