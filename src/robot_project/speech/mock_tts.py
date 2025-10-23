import time

class MockTextToSpeech:
    """Simulación de Text-to-Speech para desarrollo sin dispositivo de audio"""

    def __init__(self, audio_device, voice="es-PE-CamilaNeural", rate="+0%"):
        self.audio_device = audio_device
        self.voice = voice
        self.rate = rate
        print(f"🔧 [MOCK] TTS simulado con voz: {voice}")

    def speak_text(self, text, voice=None, rate=None):
        """Simula la conversión de texto a voz"""
        print(f"🔊 [MOCK] TTS: {text}")
        # Simula el tiempo que tomaría hablar
        time.sleep(len(text) * 0.05)  # ~0.05s por carácter

    def deliver_message(self, msg):
        """Simula la entrega de un mensaje"""
        print(f"🤖 Robot: {msg}\n")
        # En modo mock, solo imprime, no genera audio
        time.sleep(len(msg) * 0.03)
