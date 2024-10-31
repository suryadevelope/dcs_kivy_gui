import requests
import json
import configparser
import os

# Load configuration
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config/config.ini'))


# Retrieve host and port from the configuration
HOST = config.get("API", "host", fallback="http://localhost")
PORT = config.get("API", "port", fallback="3000")
APIURL = f"{HOST}:{PORT}"

def authenticate_device(mac_address):
    """
    Sends a POST request to authenticate the device and retrieve a device token.

    Args:
        mac_address (str): The MAC address of the device.

    Returns:
        dict or None: Returns the JSON response containing the device token if successful, otherwise None.
    """
    url = APIURL+"/deviceauth"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"mac": mac_address})

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        return response.json()  # Assumes response is JSON and returns it

    except requests.RequestException as e:
        print(f"Error during authentication request: {e}")
        return None
