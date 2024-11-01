import socketio
import configparser
import os
from utils.secure import Emitter
from kivy.storage.jsonstore import JsonStore


store = JsonStore("auth_info.json")

# Load configuration
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config/config.ini'))

# Retrieve host and port from the configuration
HOST = config.get("API", "host", fallback="http://localhost")
PORT = config.get("API", "port", fallback="3000")
SERVER_URL = f"{HOST}:{PORT}"

# Create a singleton Socket.IO client instance
sio = socketio.Client(
    reconnection=True,
    # serializer=Emitter
    )
# Connect to the server
def connect_to_server():
    if not sio.connected:
        try:
            print(store.get("devicetoken").get("token"))
    
            sio.connect(SERVER_URL,auth={"token":store.get("devicetoken").get("token")},transports= ['websocket'])
            print("Connected to the Socket.IO server.")
        except socketio.exceptions.ConnectionError as e:
            print(f"Socket connection error: {e}")

@sio.event
def connect():
    print("Connected to the default namespace.")

# Handle disconnection
@sio.event
def disconnect():
    print("Disconnected from the Socket.IO server.")

# Authentication response handler
@sio.on("auth_response")
def on_auth_response(data):
    print("Received authentication response:", data)
    sio.auth_response = data  # Store response for later use


# Initialize connection at the start
connect_to_server()

# Expose the singleton client instance
socket_client = sio
