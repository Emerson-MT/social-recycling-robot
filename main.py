import os
import sys
# Add src to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
# Imports
from robot_project import SerialConnection, StudentDatabase, LargeLanguageModel, RecyclingRobot, SpeechToText, TextToSpeech, HailoVision
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

# =============== MAIN FUNCTIONS ==================

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

    # Detectar si estamos en modo mock (desarrollo local)
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
    cv = HailoVision(CV_MODEL_PATH)
    ser = SerialConnection(SERIAL_CONN1, 9600, 1)
    db = StudentDatabase(DB_CONFIG)

    return RecyclingRobot("Peri", commands, AUDIO_DEVICE, AUDIO_PATHS, stt, llm, tts, cv, ser, db)

def show_test_menu():
    print('''\n--- Menú de pruebas ---
    1) Detección de proximidad
    2) Giro stepper con teclado
    3) Compuertas (servos)
    4) Clasificación de residuo (visión)
    5) Giro automático (stepper)
    6) Pulsadores (stepper)
    7) Código y base de datos
    8) Conversación con Peri
    9) Programa completo
    ''')

def get_test_input() -> int:
    try:
        return int(input("Ingrese el número de la prueba a realizar: "))
    except ValueError:
        print("Entrada inválida.")
        return -1

# ========== PROGRAMA PRINCIPAL ========
def main():
    peri = setup_robot()

    while True:
        show_test_menu()
        test = get_test_input()
        peri.set_test_num(test)
        if test == 9:
            peri.run_main_program()
        else:
            peri.run_test(test)

if __name__ == "__main__":
    main()
