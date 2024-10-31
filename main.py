from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.core.window import Window

from screens.splash_screen import SplashScreen
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen

# Screen Manager
class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        # Window.fullscreen = True
        
        # Load all KV files
        Builder.load_file("./kv/splash_screen.kv")
        Builder.load_file("./kv/login_screen.kv")
        Builder.load_file("./kv/home_screen.kv")
        
        # Screen Manager setup
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        
        return sm

if __name__ == "__main__":
    MainApp().run()
