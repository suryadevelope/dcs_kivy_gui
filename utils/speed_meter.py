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

    Speedometer:
        id: speedometer
        size_hint: 1, 1
"""

class Speedometer(Widget):
    speed = NumericProperty(0)  # Current speed value
    speed_text = StringProperty("0")  # Speed text to display above "kmph"
    numbers = []  # To keep track of the number labels

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw_speedometer, pos=self._draw_speedometer)
        Clock.schedule_once(self._draw_speedometer)
        Clock.schedule_interval(self._update_speed, 0.1)  # Update every 0.1 seconds
        self.increment = 1  # Direction of speed change

    def _update_speed(self, dt):
        """Automatically update speed."""
        # Change speed in a range between 0 and 180
        if self.speed >= 180:
            self.increment = -1  # Reverse direction
        elif self.speed <= 0:
            self.increment = 1  # Forward direction
        self.speed += self.increment
        self.speed_text = str(int(self.speed))  # Update speed text
        self._draw_speedometer()

    def _draw_speedometer(self, *args):
        """Draw the circular speedometer and its components."""
        self.canvas.clear()
        self._clear_previous_numbers()  # Clear previous numbers

        with self.canvas:
            center_x, center_y = self.center
            radius = min(self.size) * 0.90

            # Draw primary ticks (larger ticks)
            for i in range(10):  # 10 primary intervals
                angle = -135 - i * (270 / 9)  # Start from 135° and distribute over 270°
                x1 = center_x + radius * 0.80 * cos(radians(angle))
                y1 = center_y + radius * 0.80 * sin(radians(angle))
                x2 = center_x + radius * cos(radians(angle))
                y2 = center_y + radius * sin(radians(angle))

                # Apply color conditions
                if self._is_tick_touched(angle):
                    Color(1, 0, 0, 1)  # Red for glowing tick
                elif self.speed >= i * 20:
                    Color(0, 1, 0, 1)  # Green for passed ticks
                else:
                    Color(1, 1, 1, 1)  # White for default
                Line(points=[x1, y1, x2, y2], width=2)

                # Add numbers at ticks
                number = i * 20
                num_x = center_x + radius * 0.6 * cos(radians(angle))
                num_y = center_y + radius * 0.6 * sin(radians(angle))
                self._add_number(str(number), num_x, num_y)

            # Draw millimeter ticks (smaller ticks with equal spacing)
            for i in range(9):  # For each primary tick
                angle_start = -135 - i * (270 / 9)  # Start angle of the primary tick
                angle_end = -135 - (i + 1) * (270 / 9)  # End angle of the next primary tick
                for j in range(1, 10):  # 9 millimeter intervals between each primary tick
                    angle = angle_start - j * ((angle_start - angle_end) / 10)
                    x1 = center_x + radius * 0.9 * cos(radians(angle))
                    y1 = center_y + radius * 0.9 * sin(radians(angle))
                    x2 = center_x + radius * 0.95 * cos(radians(angle))
                    y2 = center_y + radius * 0.95 * sin(radians(angle))

                    # Apply color conditions
                    if self._is_tick_touched(angle):
                        Color(1, 0, 0, 1)  # Red for glowing tick
                    elif self.speed >= (i * 20 + j * 2):  # Scale millimeter ticks accordingly
                        Color(0, 1, 0, 1)  # Green for passed ticks
                    else:
                        Color(1, 1, 1, 1)  # White for default
                    Line(points=[x1, y1, x2, y2], width=1)

            # Draw glowing arc
            glow_angle_start = -135  # Start at -135° (left side)
            glow_angle_end = glow_angle_start + self.speed * (270 / 180)  # Spread the glow clockwise
            Color(0.7, 1.0, 0.5, 1)  # Green
            Line(circle=(center_x, center_y, radius, glow_angle_start, glow_angle_end),
                 width=4, cap='round')

            # Draw center circle
            center_circle_radius = radius * 0.3
            Color(0.2, 0.2, 0.2, 1)  # Dark gray
            Ellipse(pos=(center_x - center_circle_radius, center_y - center_circle_radius),
                    size=(center_circle_radius * 2, center_circle_radius * 2))

        # Add live speed text and 'km/h' label
        self._add_center_text(self.speed_text, center_x, center_y + 10)
        self._add_center_text("km/h", center_x, center_y - 5)

    def _is_tick_touched(self, tick_angle):
        """Check if the glowing arc touches a tick (primary or millimeter)."""
        glow_angle_start = -135  # Start at -135° (left side)
        glow_angle_end = glow_angle_start + self.speed * (270 / 180)
        return glow_angle_start <= tick_angle <= glow_angle_end

    def _add_number(self, text, x, y):
        """Add a number to the speedometer at the given position."""
        # Only add the number if it doesn't already exist at that position
        if (x, y) not in [(label.pos[0], label.pos[1]) for label in self.numbers]:
            number_label = Label(
                text=text,
                font_size="12sp",
                color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=(50, 50),
                pos=(x - 25, y - 25)  # Center the label around (x, y)
            )
            #self.add_widget(number_label)
            self.numbers.append(number_label)

    def _clear_previous_numbers(self):
        """Clear previous numbers from the speedometer."""
        for label in self.numbers:
            self.remove_widget(label)
        self.numbers.clear()

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
#      return Builder.load_string(KV)

#if __name__ == "__main__":
#   SpeedometerApp().run()
