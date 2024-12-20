from kivy.garden.mapview import MapView, MapSource
from kivy.app import App

class SatelliteMapApp(App):
    def build(self):
        # Define a custom MapSource for satellite tiles
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
        return mapview

# Run the app
if __name__ == "__main__":
    SatelliteMapApp().run()
