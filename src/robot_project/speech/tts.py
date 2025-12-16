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

        # --- NUEVO: Forzar volumen del hardware al 100% ---
        try:
            # Intenta subir el volumen del sistema (Master/PCM/Speaker)
            # 'amixer' es el comando de Linux para mezclar audio
            subprocess.run(["amixer", "set", "Master", "100%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # En caso de que se llame 'Speaker' o 'PCM' en el ReSpeaker:
            subprocess.run(["amixer", "-c", "3", "set", "Speaker", "100%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
            # Nota: -c 3 asume que es la tarjeta 3. Si usas 'default', la primera línea basta.
        except Exception as e:
            print(f"⚠️ No se pudo ajustar el volumen del sistema: {e}")
    
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
                # --- MODIFICADO: Agregamos '-v', '2.0' para duplicar el volumen ---
                # Ajusta el 2.0 a 1.5 o 3.0 según necesites.
                subprocess.run(["sox", "-v", "3.0", wav_path, "-t", "alsa", self.audio_device])
                
                # O si decidiste usar 'default' y 'play':
                # subprocess.run(["play", "-v", "2.0", wav_path])
            except Exception as e:
                print("❌ Error al reproducir audio:", e)
            finally:
                os.remove(mp3_path)
                os.remove(wav_path)

        asyncio.run(tts_edge())
    
    def deliver_message(self, msg):
        print(f"🤖 Robot: {msg}\n")
        self.speak_text(msg)