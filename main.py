import os
import sys
import tty
import termios
from pathlib import Path

# Forzar modo real
os.environ['ROBOT_MODE'] = 'real'

# Add src to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Imports
from robot_project import RecyclingRobot
from robot_project.configs.config_loader import load_config
from robot_project.configs.environment import is_mock_mode
from robot_project.fsm.recycling_fsm import RecyclingFSM
import signal

# Load the json configuration file
config = load_config()

# ========== CONFIGURATIONS ====================
LLM_API_KEY = config["llm"]["api_key"]
LLM_API_BASE = config["llm"]["api_base"]
LLM_MODEL = config["llm"]["model"]

STT_MODEL_PATH = config["stt"]["model_path"]
TTS_VOICE = config["tts"]["speech_voice"]
CV_MODEL_PATH = config["cv"]["model_file"]

DB_CONFIG = config["database"]

AUDIO_DEVICE = config["audio"]["device"]
AUDIO_DEVICE = "default"

SERIAL_CONN1 = config["serial"]["conn1"]

AUDIO_PATHS = config["audio_files"]

# ========== INTERRUPTION HANDLING ============================
def handle_keyboard_interrupt(signum, frame):
    print("\n🛑 Interrupción detectada.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

# ========== WIZARD OF OZ: CONFIGURACIÓN DE TERMINAL ============================
class RawMode:
    """Context manager para modo raw de terminal (no bloquea entrada)"""
    
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self
    
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

# =============== MAIN FUNCTIONS ==================

def setup_robot() -> RecyclingRobot:
    """Configura el robot con todos sus componentes"""
    commands = {
        'r': 'reciclar',
        'y': 'yo',
        't': 'tú',
        '0': 'cartón',
        '1': 'papel',
        '2': 'plástico',
        '3': 'residuo_general'
    }

    mock_mode = is_mock_mode()

    if mock_mode:
        print("=" * 60)
        print("🔧 MODO SIMULADO ACTIVADO - Usando componentes simulados")
        print("=" * 60)
        from robot_project.speech.mock_stt import MockSpeechToText as SpeechToText
        from robot_project.speech.mock_tts import MockTextToSpeech as TextToSpeech
        from robot_project.vision.mock_vision import MockComputerVision as HailoVision
        from robot_project.connections.mock_serial import MockSerialConnection as SerialConnection
        from robot_project.database.mock_database import MockStudentDatabase as StudentDatabase
        from robot_project.llm.mock_llm import MockLargeLanguageModel as LargeLanguageModel
        from robot_project.display.mock_display import MockDisplay as Display
    else:
        print("=" * 60)
        print("🤖 MODO REAL ACTIVADO - Usando hardware real")
        print("=" * 60)
        from robot_project import SerialConnection, HailoVision
        from robot_project.speech.mock_stt import MockSpeechToText as SpeechToText
        from robot_project.speech.tts import TextToSpeech
        from robot_project.database.mock_database import MockStudentDatabase as StudentDatabase
        from robot_project.llm.mock_llm import MockLargeLanguageModel as LargeLanguageModel
        from robot_project.display.display import Display
        
    # Inicializar componentes
    stt = SpeechToText(STT_MODEL_PATH)
    llm = LargeLanguageModel(LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
    tts = TextToSpeech(AUDIO_DEVICE, TTS_VOICE, "+0%")
    cv = HailoVision(model_name=CV_MODEL_PATH, zoo_url="src/robot_project/models", inference_host="@local")
    ser = SerialConnection(SERIAL_CONN1, 115200, 1)
    db = StudentDatabase(DB_CONFIG)
    display = Display()

    robot = RecyclingRobot("Peri", commands, AUDIO_DEVICE, AUDIO_PATHS, stt, llm, tts, cv, ser, db, display)

    # ========== CARGAR ASSETS DE PYGAME ==========
    print("\n" + "=" * 60)
    print("🎨 CARGANDO ASSETS PARA LA PANTALLA")
    print("=" * 60)
    
    try:
        import robot_project.display
        display_module_dir = Path(robot_project.display.__file__).parent
    except:
        display_module_dir = Path(__file__).parent / "src" / "robot_project" / "display"
    
    project_root = Path(__file__).parent
    
    animations_search_paths = [
        display_module_dir / "Animations" / "Gifs",
        project_root / "Animations" / "Gifs",
        project_root / "src" / "robot_project" / "display" / "Animations" / "Gifs",
        Path("Animations") / "Gifs",
    ]
    
    animations_dir = None
    for path in animations_search_paths:
        if path.exists() and path.is_dir():
            animations_dir = path
            print(f"📁 Directorio de animaciones encontrado: {animations_dir}")
            break
    
    if not animations_dir:
        print("⚠️  No se encontró el directorio de animaciones")
        animations_dir = Path(".")
    
    anim_scale = (800, 500)
    
    gif_assets = {
        "hibernando": "Ojo_dormilon.gif",
        "despertando_inicio": "Ojo_despierta_1.gif",
        "despertando_loop": "Ojo_despierta_2.gif",
        "neutro": "Ojo_neutro.gif",
        "feliz": "Ojo_emocion.gif",
        "despedida": "Bye2.gif",
        "error": "Ojo_error.gif",
        "enojo": "Ojo_enojo_2.gif"
    }
    
    for name, filename in gif_assets.items():
        filepath = animations_dir / filename
        robot.display.load_gif(name, str(filepath), scale=anim_scale)
    
    # Cargar imagen QR
    images_search_paths = [
        display_module_dir / "Images",
        project_root / "Images",
        project_root / "src" / "robot_project" / "display" / "Images",
        Path("Images"),
    ]
    
    images_dir = None
    for path in images_search_paths:
        if path.exists() and path.is_dir():
            images_dir = path
            print(f"📁 Directorio de imágenes encontrado: {images_dir}")
            break
    
    if images_dir:
        qr_path = images_dir / "QR_Prueba.png"
    else:
        qr_path = None
        for search_path in images_search_paths:
            potential_qr = search_path / "QR_Prueba.png"
            if potential_qr.exists():
                qr_path = potential_qr
                break
        
        if not qr_path:
            qr_path = Path("QR_Prueba.png")
    
    try:
        robot.display.load_image("qr", str(qr_path), scale=(200, 200))
    except Exception as e:
        print(f"⚠️  No se pudo cargar la imagen QR: {e}")
    
    print("=" * 60)
    print("✅ ASSETS CARGADOS")
    print("=" * 60 + "\n")
    
    return robot

def show_test_menu():
    print('''\n--- Menú de pruebas ---
    1) Detección de proximidad
    2) Giro stepper con teclado
    3) Compuertas (servos)
    4) Clasificación de residuo (visión)
    5) Giro automático (stepper)
    6) Pulsadores (stepper)
    7) Código y base de datos
    8) Modo Golden
    9) Programa completo (WIZARD OF OZ MODE)
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
            # ========== WIZARD OF OZ MODE ==========
            print("\n" + "="*60)
            print("🎭 INICIANDO MODO WIZARD OF OZ")
            print("="*60)
            print("\n⚠️  IMPORTANTE: Terminal en modo RAW")
            print("   Las teclas se leen sin presionar Enter\n")
            
            # Crear FSM
            fsm = RecyclingFSM(peri)
            
            # Entrar en modo raw (sin bloqueo)
            with RawMode():
                fsm.run()
            # ==========================================
        else:
            peri.run_test(test)

if __name__ == "__main__":
    main()
