from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivymd.app import MDApp
from math import sin, cos, radians

KV = """
BoxLayout:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1  # Black background
        Rectangle:
            pos: self.pos
            size: self.size

    Fuel_meter:
        id: speedometer
        size_hint: 1, 1
"""
 
class Fuel_meter(Widget):
    speed = NumericProperty(0)  # Current speed value
    speed_text = StringProperty("0")  # Speed text to display above "kmph"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw_speedometer, pos=self._draw_speedometer)
        Clock.schedule_once(self._draw_speedometer)
        Clock.schedule_interval(self._update_speed, 0.1)  # Update every 0.1 seconds

        self.increment = 1  # Direction of speed change
        self.primary_tick_angles = []  # To store primary tick angles
        self.millimeter_tick_angles = []  # To store millimeter tick angles

    def _update_speed(self, dt):
        """Automatically update speed."""
        # Change speed in a range between 0 and 180
        if self.speed >= 100:
            self.increment = -1  # Reverse direction
        elif self.speed <= 0:
            self.increment = 1  # Forward direction
        self.speed += self.increment
        self.speed_text = str(int(self.speed))  # Update speed text
        self._draw_speedometer()

    def _draw_speedometer(self, *args):
        """Draw the semicircular speedometer and its components."""
        self.canvas.clear()
        self.primary_tick_angles.clear()
        self.millimeter_tick_angles.clear()
        
        with self.canvas:
            center_x, center_y = self.center
            radius = min(self.size) * 0.45

            # Draw background arc
            Color(255, 255, 255, 255)  # Dark gray
            Ellipse(pos=(center_x - radius, center_y - radius),
                    size=(radius * 2, radius * 2),
                    angle_start=270, angle_end=270)

            # Draw outer arc
            Color(136, 136, 136, 255)  # Gray
            Ellipse(pos=(center_x - radius, center_y - radius),
                    size=(radius * 2, radius * 2),
                    angle_start=270, angle_end=270)

            # Draw primary ticks
            angle_start = 270
            angle_end = 90
            for i in range(10):  # 10 intervals
                angle = angle_start + i * (angle_end - angle_start) / 9
                self.primary_tick_angles.append(angle)
                x1 = center_x + radius * 0.85 * cos(radians(angle - 90))
                y1 = center_y + radius * 0.85 * sin(radians(angle - 90))
                x2 = center_x + radius * cos(radians(angle - 90))
                y2 = center_y + radius * sin(radians(angle - 90))

                # Highlight tick if touched by the glowing arc
                if self._is_tick_touched(angle):
                    Color(0.1, 0.1, 0.1, 1)  # Red highlight
                else:
                    Color(0.7, 1.0, 0.5, 1)  # Yellow for normal ticks
                Line(points=[x1, y1, x2, y2], width=2)

                # Add numbers at ticks
                number = i * 0
                num_x = center_x + radius * 0.7 * cos(radians(angle - 90))
                num_y = center_y + radius * 0.7 * sin(radians(angle - 90))
                #self._add_number(str(number), num_x, num_y)

                # Draw millimeter ticks between primary ticks
                if i < 9:  # No millimeter ticks after the last primary tick
                    next_angle = angle_start + (i + 1) * (angle_end - angle_start) / 9
                    for j in range(1, 10):  # 9 millimeter ticks between each primary tick
                        millimeter_angle = angle + j * (next_angle - angle) / 10
                        self.millimeter_tick_angles.append(millimeter_angle)
                        mm_x1 = center_x + radius * 0.9 * cos(radians(millimeter_angle - 90))
                        mm_y1 = center_y + radius * 0.9 * sin(radians(millimeter_angle - 90))
                        mm_x2 = center_x + radius * 0.95 * cos(radians(millimeter_angle - 90))
                        mm_y2 = center_y + radius * 0.95 * sin(radians(millimeter_angle - 90))

                        # Highlight millimeter tick if touched by the glowing arc
                        if self._is_tick_touched(millimeter_angle):
                            Color(0.1, 0.1, 0.1, 1)  # Red highlight
                        else:
                            Color(0.7, 1.0, 0.5, 1)  # White for normal millimeter ticks
                        Line(points=[mm_x1, mm_y1, mm_x2, mm_y2], width=1)

            # Draw glowing arc
            light_angle = 270 + (self.speed * (180 / 180))  # Adjusted for movement
            Color(0.7, 1.0, 0.5, 1)  # Green
            Line(circle=(center_x, center_y, radius, 270, light_angle),
                 width=2, cap='round')

            # Draw center circle
            center_circle_radius = radius * 0.5
            Color(0.2, 0.2, 0.2, 1)  # Dark circle
            Ellipse(pos=(center_x - center_circle_radius, center_y - center_circle_radius),
                    size=(center_circle_radius * 2, center_circle_radius * 2))

        # Add live speed text and 'kmph' label
        self._add_center_text(self.speed_text, center_x, center_y + 10)
        self._add_center_text("petrol", center_x, center_y - 20)

    def _is_tick_touched(self, tick_angle):
        """Check if the glowing arc touches a tick."""
        glow_angle = 170 - (self.speed * (180 / 180))  # Angle of the glowing arc
        return abs(tick_angle - glow_angle) <100 # Small threshold for highlighting

    def _add_number(self, text, x, y):
        """Add a number to the speedometer at the given position."""
        number_label = Label(
            text=text,
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(50, 50),
            pos=(x - 25, y - 25)  # Center the label around (x, y)
        )
        #self.add_widget(number_label)

    def _add_center_text(self, text, x, y):
        """Add text to the center of the speedometer."""
        center_label = Label(
            text=text,
            font_size="12sp" if text != self.speed_text else "15sp",
            bold=True,
            color=(1, 1, 1, 1),  # White text
            size_hint=(None, None),
            size=(100, 50),
            pos=(x - 50, y - 25)  # Center the label at the position
        )
        self.add_widget(center_label)

#class SpeedometerApp(MDApp):
#   def build(self):
#        return Builder.load_string(KV)

#if __name__ == '__main__':
#   SpeedometerApp().run()
