import time

class MockSpeechToText:
    """Simulación de Speech-to-Text para desarrollo sin micrófono"""

    def __init__(self, model_path):
        self.stt_model = None
        self.stt_recognizer = None
        print("🔧 [MOCK] Modelo STT simulado")
        print(f"🔧 [MOCK] Ruta del modelo: {model_path}")

    def load_stt_model(self, model_path):
        """Simula la carga del modelo"""
        print("⏳ [MOCK] Cargando modelo de Vosk...")
        time.sleep(0.5)
        self.stt_model = "mock_model"
        self.stt_recognizer = "mock_recognizer"
        print("✅ [MOCK] Modelo cargado")

    def listen_to_user(self):
        """
        Simula la escucha del usuario.
        En modo mock, el input de consola será la única forma de entrada.
        """
        print("🎤 [MOCK] Esperando entrada de consola (el micrófono está simulado)...")
        # Retorna None para que solo funcione la entrada de consola
        return None
