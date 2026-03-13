import queue
import subprocess
import os
import threading
import time
from robot_project.llm import LargeLanguageModel
from robot_project.speech import TextToSpeech, SpeechToText
from robot_project.vision import ComputerVision
from robot_project.connections import SerialConnection
from robot_project.display import Display
from robot_project.configs.environment import is_mock_mode

class Robot:

    def __init__(self, name, commands, audio_device, stt: SpeechToText, llm: LargeLanguageModel, 
                 tts: TextToSpeech, cv: ComputerVision, ser: SerialConnection, display: Display
                 ):
        self.name = name
        self.audio_device = audio_device   
        self.stt = stt # Speech to text (STT)
        self.tts = tts # Texto to Speech (TTS) 
        self.llm = llm # Large Language Model (LLM)
        self.cv = cv # Computer Vision 
        self.ser = ser # Serial connection
        self.display = display
        # Command queues
        self.commands = commands or {}
        self.command_queue = queue.Queue()
        # Threads
        self.listen_thread = None
        self.console_thread = None
        self.stop_event = threading.Event()
    
    def play_audio(self, mp3_path):
        if is_mock_mode():
            print(f"🔊 [MOCK] Reproduciendo audio: {os.path.basename(mp3_path)}")
            time.sleep(0.5)
            return

        # En lugar de sox + alsa, usamos ffplay que es más robusto con BT
        # -nodisp: sin ventana, -autoexit: cierra al terminar, -loglevel: silencio
        print(f"🔊 Reproduciendo en parlante Bluetooth...")
        try:
            # Si usas PulseAudio (estándar en Raspberry Pi OS moderno):
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", mp3_path])
            
            # SI prefieres seguir con sox, asegúrate que audio_device sea 'bluealsa' o 'default'
            # subprocess.run(["play", "-v", "1.0", mp3_path]) 
        except Exception as e:
            print("❌ Error al reproducir audio:", e)

        def print_commands(self):
            print("\n[Comandos disponibles]:")
            for k, v in self.commands.items():
                print(f"  {k}: {v}")


    def console_listener(self):
        while not self.stop_event.is_set():
            try:
                self.print_commands()
                user_input = input("[Consola] Escribe un comando:").strip()

                if user_input:
                    # Usa el valor del diccionario si existe; si no, usa el mismo input
                    command = self.commands.get(user_input, user_input)
                    # Se carga el valor en el queue
                    self.command_queue.put(command)
                    self.stop_event.set()
                    break
                else:
                    print("⚠️ Entrada vacía. Por favor, escribe un comando válido.")

            except EOFError:
                self.stop_event.set()
                break
            except KeyboardInterrupt:
                print("\n🔴 Interrupción detectada (Ctrl+C en consola)")
                self.stop_event.set()
                break
            
    def _listen_and_queue(self):
        text = self.stt.listen_to_user()
        if text:
            self.command_queue.put(text)
            self.stop_event.set()

    def get_response(self):
        while True:
            if self.stop_event.is_set() and self.command_queue.empty():
                return None  # Sale si se detuvo todo y no hay nada en la cola
            try:
                command = self.command_queue.get_nowait()
                if command:  # Solo si el comando no es None ni cadena vacía
                    print(f"Comando recibido: {command}")
                    return command
            except queue.Empty:
                pass

            time.sleep(0.1)

    def start_listening_threads(self):
        self.stop_event.clear()

        if self.listen_thread is None or not self.listen_thread.is_alive():
            self.listen_thread = threading.Thread(target=self._listen_and_queue, daemon=True)
            self.listen_thread.start()

        if self.console_thread is None or not self.console_thread.is_alive():
            self.console_thread = threading.Thread(target=self.console_listener, daemon=True)
            self.console_thread.start()