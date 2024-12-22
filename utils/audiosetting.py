
import threading
from gtts import gTTS

# Import pygame for playing the converted audio
import pygame

pygame.mixer.init()

class text_sound():

    def __init__(self):
        self.filename="speechaudio.mp3"
        self.language = 'en'

    def play(self,text):    
        self.myobj = gTTS(text=text, lang=self.language, slow=False)
        self.myobj.save(self.filename)
        threading.Thread(target=self.sound,daemon=True).start()

    def sound(self):
        # Load the mp3 file
        pygame.mixer.music.load(self.filename)

        # Play the loaded mp3 file
        pygame.mixer.music.play()

        # Wait until the audio is finished
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)