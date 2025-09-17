import os
from gtts import gTTS
import tempfile
import asyncio
import edge_tts
import subprocess

class TextToSpeech:
    def __init__(self, audio_device, voice="es-PE-CamilaNeural", rate="+0%"):
        self.audio_device = audio_device
        self.voice = voice
        self.rate = rate
    
    def speak_text(self, text, voice=None, rate=None):
        voice = voice or self.voice
        rate = rate or self.rate
        #voice = "es-MX-DaliaNeural"
        async def tts_edge():
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f_mp3:
                mp3_path = f_mp3.name

            wav_path = mp3_path.replace(".mp3", ".wav")

            await communicate.save(mp3_path)

            # Convertir a WAV con ffmpeg
            subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if not self.audio_device:
                print("❌ No se encontró el dispositivo de audio.")
                return

            print(f"🔊 Reproduciendo en: {self.audio_device}")
            try:
                subprocess.run(["sox", wav_path, "-t", "alsa", self.audio_device])
            except Exception as e:
                print("❌ Error al reproducir audio:", e)
            finally:
                os.remove(mp3_path)
                os.remove(wav_path)

        asyncio.run(tts_edge())
    
    def deliver_message(self, msg):
        print(f"🤖 Robot: {msg}\n")
        self.speak_text(msg)