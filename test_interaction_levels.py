#!/usr/bin/env python3
"""
Script de prueba para el sistema de niveles de interacción.
Este script te permite probar el flujo completo en modo simulado.
"""

import os
import sys

# Forzar modo mock y niveles de interacción
os.environ['ROBOT_MODE'] = 'sim'
# Si quieres probar el modo legacy, descomenta la siguiente línea:
# os.environ['ROBOT_MODE'] = 'real'

# Add src to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from robot_project import RecyclingRobot
from robot_project.configs.config_loader import load_config
from robot_project.configs.environment import is_mock_mode
import signal

# Load the json configuration file
config = load_config()

# ========== CONFIGURATIONS ====================
LLM_API_KEY = config["llm"]["api_key"]
LLM_API_BASE = config["llm"]["api_base"]
LLM_MODEL = config["llm"]["model"]

STT_MODEL_PATH = config["stt"]["model_path"]
TTS_VOICE = config["tts"]["speech_voice"]
CV_MODEL_PATH = config["cv"]["model_path"]

DB_CONFIG = config["database"]

AUDIO_DEVICE = config["audio"]["device"]

SERIAL_CONN1 = config["serial"]["conn1"]

AUDIO_PATHS = config["audio_files"]

# ========== INTERRUPTION HANDLING ============================
def handle_keyboard_interrupt(signum, frame):
    print("\n🛑 Interrupción detectada.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

# =============== MAIN TEST ==================

def setup_robot() -> RecyclingRobot:
    commands = {
        'r': 'reciclar',
        'y': 'yo',
        't': 'tú',
        '0': 'cartón',
        '1': 'papel',
        '2': 'plástico',
        '3': 'residuo_general'
    }

    # Detectar si estamos en modo mock
    mock_mode = is_mock_mode()

    if mock_mode:
        print("=" * 60)
        print("🔧 MODO DESARROLLO - Usando componentes simulados")
        print("=" * 60)
        from robot_project.speech.mock_stt import MockSpeechToText as SpeechToText
        from robot_project.speech.mock_tts import MockTextToSpeech as TextToSpeech
        from robot_project.vision.mock_vision import MockComputerVision as ComputerVision
        from robot_project.connections.mock_serial import MockSerialConnection as SerialConnection
        from robot_project.database.mock_database import MockStudentDatabase as StudentDatabase
        from robot_project.llm.mock_llm import MockLargeLanguageModel as LargeLanguageModel
    else:
        print("=" * 60)
        print("🤖 MODO PRODUCCIÓN - Usando hardware real")
        print("=" * 60)
        from robot_project import SerialConnection, SpeechToText, TextToSpeech, ComputerVision, StudentDatabase, LargeLanguageModel

    stt = SpeechToText(STT_MODEL_PATH)
    llm = LargeLanguageModel(LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
    tts = TextToSpeech(AUDIO_DEVICE, TTS_VOICE, "+0%")
    cv = ComputerVision(CV_MODEL_PATH)
    ser = SerialConnection(SERIAL_CONN1, 9600, 1)
    db = StudentDatabase(DB_CONFIG)

    return RecyclingRobot("Peri", commands, AUDIO_DEVICE, AUDIO_PATHS, stt, llm, tts, cv, ser, db)

def main():

    input("Presiona ENTER para iniciar el test...")

    peri = setup_robot()

    # Ejecutar programa principal (usará niveles o legacy según configuración)
    peri.run_main_program()

if __name__ == "__main__":
    main()
