import logging
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.core.window import Window

from screens.allappscreen import AllappsScreen
from screens.full_map import Fullmapscreen
from screens.splash_screen import SplashScreen
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition,FadeTransition,FallOutTransition

from utils.audiosetting import text_sound


# Window.fullscreen = True  # This forces the app into full-screen mode.


# Screen Manager
class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Logger.setLevel(logging.DEBUG)
        
        # Load all KV files
        Builder.load_file("./kv/splash_screen.kv")
        Builder.load_file("./kv/login_screen.kv")
        Builder.load_file("./kv/home_screen.kv")
        Builder.load_file("./kv/allappscreen.kv")
        Builder.load_file("./kv/full_map.kv")
        
        # Screen Manager setup
        sm = ScreenManager()
       
        # SlideTransition (left to right)
        sm.transition = SlideTransition(direction="left")

        # FadeTransition
        # sm.transition = FadeTransition(duration=0.1)

        # SwapTransition
        # sm.transition = SwapTransition()

        # FallOutTransition (a falling transition)
        # sm.transition = FallOutTransition()

        
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AllappsScreen(name="allapps"))
        sm.add_widget(Fullmapscreen(name="fullmap"))
        self.audio=text_sound()
        self.audio.play("welcome to D C S, Drive care system")
        

        sm.current = "home"
        
        return sm

if __name__ == "__main__":
    MainApp().run()
