import queue
import sys
import json
import pyaudio
import numpy as np
from vosk import Model, KaldiRecognizer

class SpeechToText:
    def __init__(self, model_path, device_name="ReSpeaker", rate=16000, channels=6, chunk=1024):
        
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.device_index = self.find_device(device_name)

        if self.device_index is None:
            raise RuntimeError(f"❌ No se encontró un dispositivo que contenga: {device_name}")

        # cargar modelo
        self.stt_model = None
        self.stt_recognizer = None
        self.load_stt_model(model_path)

    def load_stt_model(self, model_path):
        try:
            print("⏳ Cargando modelo de Vosk...")
            self.stt_model = Model(model_path)
            self.stt_recognizer = KaldiRecognizer(self.stt_model, self.rate)
            print("✅ Modelo cargado")
        except Exception as e:
            print(f"❌ Error al cargar el modelo STT: {e}")
            raise
    
    @staticmethod
    def find_device(name_hint="ReSpeaker"):
        import pyaudio
        p = pyaudio.PyAudio()
        device_index = None

        print("🔍 Buscando dispositivos...")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"{i}: {info['name']} ({info['maxInputChannels']} canales)")
            if name_hint.lower() in info['name'].lower():
                device_index = i
        p.terminate()
        return device_index

    def listen_to_user(self):
        q = queue.Queue()

        def callback(in_data, frame_count, time_info, status):
            if status:
                print(status, file=sys.stderr)

            # Convertir bytes -> numpy array
            samples = np.frombuffer(in_data, dtype=np.int16)
            samples = samples.reshape(-1, self.channels)

            # Tomar canal 0 (procesado por el ReSpeaker)
            selected = samples[:, 0]

            # Volver a bytes (mono, int16)
            q.put(selected.tobytes())

            return (None, pyaudio.paContinue)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        input_device_index=self.device_index,
                        frames_per_buffer=self.chunk,
                        stream_callback=callback)

        print("🎤 Habla ahora (Ctrl+C para cancelar)...")
        stream.start_stream()

        try:
            while True:
                try:
                    data = q.get(timeout=0.3)
                    if self.stt_recognizer.AcceptWaveform(data):
                        result = self.stt_recognizer.Result()
                        text = json.loads(result)["text"]
                        if text:
                            return text
                except queue.Empty:
                    continue
        except KeyboardInterrupt:
            print("🔴 Interrupción detectada (Ctrl+C)")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
