import os
from gtts import gTTS
import tempfile
import asyncio
import edge_tts
import subprocess

class TextToSpeech:
    def __init__(self, audio_device="default", voice="en-US-AvaNeural", rate="+0%"):
        self.audio_device = audio_device
        self.voice = voice
        self.rate = rate
        # El volumen de hardware Bluetooth se suele controlar desde el celular/parlante 
        # o vía 'bluetoothctl', no por amixer fácilmente.

    def speak_text(self, text, voice=None, rate=None):
        voice = voice or self.voice
        rate = rate or self.rate

        async def tts_edge():
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f_mp3:
                mp3_path = f_mp3.name

            await communicate.save(mp3_path)

            print(f"🔊 Generando voz y enviando a Bluetooth...")
            try:
                # Usar ffplay con filtro de volumen (af_volume) si necesitas más potencia
                # 'volume=2.0' duplica el volumen digitalmente
                subprocess.run([
                    "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                    "-af", "volume=2.0", mp3_path
                ])
            except Exception as e:
                print("❌ Error al reproducir audio:", e)
            finally:
                if os.path.exists(mp3_path):
                    os.remove(mp3_path)

        asyncio.run(tts_edge())
    
    def deliver_message(self, msg):
        print(f"🤖 Robot: {msg}\n")
        self.speak_text(msg)