from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar

class MainScreen(Screen):
    grid_layout = ObjectProperty()

    def add_items(self):
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
