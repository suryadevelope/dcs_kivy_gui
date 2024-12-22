import json
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.toolbar import MDTopAppBar


class AllappsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load JSON data
        self.json_data = None
        with open("/home/dcs/Desktop/dcs_kivy_gui/assets/allapps.json", "r") as f:
            self.json_data = json.load(f)
        self.update_grid()
        self.updatetitlebar()
    
    def update_grid(self):
        """Populate the grid with dynamic content from JSON data."""
        grid_layout = self.ids.grid_layout
        for item in self.json_data:
            # Create a BoxLayout for each item to hold the image and label
            item_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(100, 120))

            # Add image
            image = Image(source=item["image"], size_hint=(None, None), size=(80, 80))
            item_layout.add_widget(image)

            # Add title label below the image
            label = MDLabel(text=item["title"], theme_text_color="Secondary", halign="center")
            item_layout.add_widget(label)

            card = MDCard(size_hint=(None, None), size=(120, 130), padding=10, elevation=5, radius=[15])
            card.add_widget(item_layout)

            # Add the card to the grid layout
            grid_layout.add_widget(card)

    
    def updatetitlebar(self):
        self.ids.titlebar.add_widget(
                MDTopAppBar(
                    type_height="small",
                    headline_text=f"Headline {'small'.lower()}",
                    md_bg_color="#2d2734",
                    left_action_items= [["arrow-left", self.on_back]],
                    # right_action_items=[
                    #     ["attachment", lambda x: x],
                    #     ["calendar", lambda x: x],
                    #     ["dots-vertical", lambda x: x],
                    # ],
                    title="Menu"
                )
            )
    def on_back(self, instance):
        # Go back to the previous screen
        if self.manager.current != 'home':
            self.manager.current = 'home'