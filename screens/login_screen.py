from kivy.uix.screenmanager import Screen
from kivy.core.image import Image as CoreImage
from io import BytesIO
import qrcode

from server import socket_con



class LoginScreen(Screen):
    def generate_qr(self):

        qrcodedata = socket_con.get_qr_data(socket_con.socket_client, "80:00:00:00:00:01")
        print("surya",qrcodedata)

        # Generate a QR code
        qr = qrcode.make(qrcodedata)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        self.ids.qr_code_image.texture = CoreImage(buffer, ext='png').texture

    def validate_login(self):
        # Placeholder for authentication logic
        self.manager.current = "home"
