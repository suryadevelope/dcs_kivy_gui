# import pyttsx3
# import sounddevice as sd
# import numpy as np
# import io

# def text_to_speech_and_play(text, rate=200, volume=1.0, voice_gender="male", device_index=0):
#     """
#     Converts text to speech and plays it on the specified device (HDMI or other).
    
#     Args:
#         text (str): The text to convert to speech.
#         rate (int): Speed of the speech (default 200).
#         volume (float): Volume of the speech (0.0 to 1.0, default 1.0).
#         voice_gender (str): Gender of the voice ("male" or "female", default "male").
#         device_index (int): The device index to output the audio (HDMI or other).
#     """
#     # Initialize the text-to-speech engine
#     engine = pyttsx3.init()
    
#     # Set properties
#     engine.setProperty('rate', rate)
#     engine.setProperty('volume', volume)
    
#     # Select voice based on gender
#     voices = engine.getProperty('voices')
#     if voice_gender.lower() == "female":
#         engine.setProperty('voice', voices[1].id)  # Female voice
#     else:
#         engine.setProperty('voice', voices[0].id)  # Male voice
    
#     # Create an in-memory byte buffer to hold the audio data
#     audio_buffer = io.BytesIO()
    
#     # Redirect pyttsx3 output to the in-memory buffer
#     engine.save_to_file(text, audio_buffer)
#     engine.runAndWait()
    
#     # Rewind the buffer to the start
#     audio_buffer.seek(0)
    
#     # Read audio data from the buffer (assuming WAV format)
#     audio_data = np.frombuffer(audio_buffer.read(), dtype=np.int16)
    
#     # Play the audio on the selected device
#     print("Playing text-to-speech audio...")
#     sd.play(audio_data, samplerate=44100, device=device_index)
#     sd.wait()  # Wait until the playback is finished
#     print("Audio playback finished.")

# # Example Usage
# if __name__ == "__main__":
#     text = input("Enter the text you want to convert to speech: ")
#     hdmi_index = 0  # Replace with your actual HDMI device index
#     text_to_speech_and_play(text, rate=200, volume=1.0, voice_gender="male", device_index=hdmi_index)







# Import the required module for text 
# to speech conversion
from gtts import gTTS

# Import pygame for playing the converted audio
import pygame

# The text that you want to convert to audio
mytext = 'person identified'

# Language in which you want to convert
language = 'en'

# Passing the text and language to the engine, 
# here we have marked slow=False. Which tells 
# the module that the converted audio should 
# have a high speed
myobj = gTTS(text=mytext, lang=language, slow=False)

# Saving the converted audio in a mp3 file named
# welcome 
myobj.save("welcome.mp3")

# Initialize the mixer module
pygame.mixer.init()

# Load the mp3 file
pygame.mixer.music.load("/home/dcs/Desktop/dcs_kivy_gui/welcome.mp3")

# Play the loaded mp3 file
pygame.mixer.music.play()

# Wait until the audio is finished
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)