# import json
# import base64
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# from Crypto.Random import get_random_bytes

# SECRET_KEY = bytes.fromhex('a4e49fdf924c834090271dae2f6019f7b91ebbcbc391c34e53c26031fa09d33b')  # 32 bytes for AES-256

# class CustomPacket:
#     def __init__(self, nsp=None, type_=None, data=None,namespace=None):
#         self.nsp = nsp or "/"
#         self.type_ = type_
#         self.data = data

#     def encode(self):
#         # Encrypt the data with AES CBC mode and a random IV
#         combined_data = self.data

#         if (self.nsp == "/" and self.type_ == 3):
            
#             cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
#             iv = cipher.iv
#             encrypted_data = cipher.encrypt(pad(json.dumps(self.data).encode('utf-8'), AES.block_size))
            
#             # Encode IV and encrypted data with Base64
#             encoded_iv = base64.b64encode(iv).decode('utf-8')
#             encoded_encrypted_data = base64.b64encode(encrypted_data).decode('utf-8')
            
#             # Combine IV and encrypted data
#             combined_data = encoded_iv + encoded_encrypted_data

#         # Create and return the encoded packet
#         encoded_packet = {
#             "nsp": self.nsp,
#             "type": self.type_,
#             "data": combined_data
#         }
#         return [json.dumps(encoded_packet)]

#     @classmethod
#     def decode(cls, data):
#         packet = json.loads(data)
#         nsp = packet.get("nsp")
#         type_ = packet.get("type")
#         combined_data = packet.get("data")

#         # Extract IV and encrypted data
#         iv = base64.b64decode(combined_data[:24])  # IV is first 24 characters in Base64
#         encrypted_data = base64.b64decode(combined_data[24:])

#         # Decrypt data
#         cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
#         decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        
#         # Load JSON from decrypted data
#         decrypted_json = json.loads(decrypted_data.decode('utf-8'))

#         return cls(nsp=nsp, type_=type_, data=decrypted_json)


import json
from cryptography.fernet import Fernet
from socketio import Client

class Emitter:
    def __init__(self):
        self._callbacks = {}

    def on(self, event, fn):
        self._callbacks.setdefault(event, []).append(fn)

    def once(self, event, fn):
        def on(*args):
            self.off(event, on)
            fn(*args)

        self.on(event, on)

    def off(self, event, fn=None):
        if event in self._callbacks:
            if fn is None:
                del self._callbacks[event]
            else:
                self._callbacks[event] = [cb for cb in self._callbacks[event] if cb != fn]

    def emit(self, event, *args):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                callback(*args)

    def listeners(self, event):
        return self._callbacks.get(event, [])

    def has_listeners(self, event):
        return len(self.listeners(event)) > 0


class Decoder(Emitter):
    def __init__(self, key):
        super().__init__()
        self.cipher = Fernet(key)

    def decrypt(self, data):
        return self.cipher.decrypt(data.encode()).decode()

    def add(self, chunk):
        packet = json.loads(chunk)
        if packet['nsp'] == "/" and packet['type'] == 3:
            data = packet['data']
            decrypted = self.decrypt(data)
            data = json.loads(decrypted) if isinstance(decrypted, str) else data
            packet['data'] = data
        
        if self.is_packet_valid(packet):
            self.emit("decoded", packet)
        else:
            raise ValueError("invalid format")

    def is_packet_valid(self, packet):
        nsp = packet['nsp']
        id = packet.get('id')
        is_namespace_valid = isinstance(nsp, str)
        is_ack_id_valid = id is None or isinstance(id, int)

        if not is_namespace_valid or not is_ack_id_valid:
            return False

        packet_type = packet['type']
        data = packet['data']
        if packet_type == 0:  # CONNECT
            return data is None or isinstance(data, dict)
        elif packet_type == 1:  # DISCONNECT
            return data is None
        elif packet_type == 2:  # EVENT
            return isinstance(data, list) and len(data) > 0
        elif packet_type == 3:  # ACK
            return isinstance(data, list)
        elif packet_type == 4:  # CONNECT_ERROR
            return isinstance(data, dict)
        else:
            return False


class Encoder:
    def __init__(self, key,data=None):
        self.cipher = Fernet(key)

    def encode(self, packet):
        nsp = packet['nsp']
        packet_type = packet['type']
        if nsp == "/" and packet_type == 3:
            data = packet['data']
            encrypted_data = self.encrypt(json.dumps(data))
            packet['data'] = encrypted_data
        return [json.dumps(packet)]

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()


# Example usage
if __name__ == "__main__":
    # Generate a key for encryption/decryption
    key = Fernet.generate_key()
    decoder = Decoder(key)
    encoder = Encoder(key)

    # Example packet
    packet = {
        "nsp": "/",
        "type": 3,
        "data": {"message": "Hello, world!"}
    }

    # Encode and then decode the packet
    encoded_packet = encoder.encode(packet)
    print("Encoded Packet:", encoded_packet)

    # Simulate receiving the chunk
    decoder.add(encoded_packet[0])