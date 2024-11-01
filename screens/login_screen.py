import base64
import json
from kivy.uix.screenmanager import Screen
from kivy.core.image import Image as CoreImage
from io import BytesIO
import segno
from kivy.clock import Clock

from server import socket_con



class LoginScreen(Screen):
    def generate_qr(self):

        socket_con.socket_client.emit("init_connect", {"data":"80:00:00:00:00:01"},callback=self.onresponse)
        
        
    def onresponse(self,sts,payload):
        # Generate a QR code
        print(sts)
        if(sts==None):
            json_data = json.dumps(payload).encode('utf-8')
    
            # Convert JSON data to Base64
            base64_data = base64.b64encode(json_data).decode('utf-8')
                
            Clock.schedule_once(lambda dt: self.update_qr_code(base64_data))

    def update_qr_code(self, base64_data):
            qr = segno.make(base64_data)

            # Save QR code to a buffer
            buffer = BytesIO()
            qr.save(buffer, kind='png', scale=5,dark="darkblue")  # Adjust 'scale' to change the size
            buffer.seek(0)
            
            # Display QR code in Kivy
            self.ids.qr_code_image.texture = CoreImage(buffer, ext='png').texture
            @socket_con.socket_client.on("onqrauthsuccess")
            def on_auth_response(data):
                print("qr success response:", data)
                
    def validate_login(self):
        # Placeholder for authentication logic
        self.manager.current = "home"
