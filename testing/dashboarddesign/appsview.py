import json
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image

class Appsview():
    def __init__(self):
        # Load JSON data
        self.json_data = None
        with open("/home/dcs/Desktop/dcs_kivy_gui/testing/dashboarddesign/allapps.json", "r") as f:
            self.json_data = json.load(f)
    
    def update_grid(self,grid_layout):
        """Populate the grid with dynamic content from JSON data."""
        
        for item in self.json_data:
            # Add image
            image = Image(source=item["image"], size_hint=(None, None), size=(80, 80))
            grid_layout.add_widget(image)
            
            # Add title label
            label = MDLabel(text=item["title"], theme_text_color="Secondary", halign="center")
            grid_layout.add_widget(label)

    