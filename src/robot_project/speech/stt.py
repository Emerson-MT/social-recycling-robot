import queue
import sys
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from ultralytics import YOLO

class SpeechToText:
    def __init__(self, model_path):
        # cargar modelo, etc.
        self.stt_model = None
        self.stt_recognizer = None
        self.load_stt_model(model_path)
    
    def load_stt_model(self, model_path):
        try:
            print("⏳ Cargando modelo de Vosk...")
            self.stt_model = Model(model_path)
            self.stt_recognizer = KaldiRecognizer(self.stt_model, 16000)
            print("✅ Modelo cargado")
        except Exception as e:
            print(f"❌ Error al cargar el modelo STT: {e}")
            raise
    
    def listen_to_user(self):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        print("🎤 Habla ahora (Ctrl+C para cancelar)...")

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                            channels=1, callback=callback):
            while True:
                try:
                    data = q.get(timeout=0.3)
                    if self.stt_recognizer.AcceptWaveform(data):
                        result = self.stt_recognizer.Result()
                        text = json.loads(result)["text"]
                        if text:
                            return text
                except queue.Empty:
                    continue  # Esperar más datos
                except KeyboardInterrupt:
                    print("🔴 Interrupción detectada (Ctrl+C)")
                    break