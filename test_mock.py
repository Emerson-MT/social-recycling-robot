#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que todos los mocks funcionan correctamente.
Ejecuta: python test_mock.py
"""

import os
import sys

# Add src to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

def test_environment():
    """Prueba la detección de entorno"""
    print("=" * 60)
    print("🧪 Probando detección de entorno...")
    print("=" * 60)
    from robot_project.configs.environment import is_mock_mode, get_environment

    env = get_environment()
    is_mock = is_mock_mode()

    print(f"Entorno detectado: {env}")
    print(f"¿Modo mock?: {is_mock}")
    print("✅ Detección de entorno funcionando\n")
    return is_mock

def test_mock_serial():
    """Prueba MockSerialConnection"""
    print("=" * 60)
    print("🧪 Probando MockSerialConnection...")
    print("=" * 60)
    from robot_project.connections.mock_serial import MockSerialConnection

    ser = MockSerialConnection("/dev/ttyUSB0", 9600, 1)
    ser.connect()
    ser.send("PRUEBA:1\n")
    valor = ser.wait_for_message("POS:")
    print(f"Valor recibido: {valor}")
    ser.disconnect()
    print("✅ MockSerialConnection funcionando\n")

def test_mock_vision():
    """Prueba MockComputerVision"""
    print("=" * 60)
    print("🧪 Probando MockComputerVision...")
    print("=" * 60)
    from robot_project.vision.mock_vision import MockComputerVision

    cv = MockComputerVision("modelo_fake.pt")
    resultado = cv.classify(tiempo_limite=1)
    if resultado:
        class_id, class_name, confidence = resultado
        print(f"Clasificación: {class_name} (id={class_id}, conf={confidence:.2f})")
    print("✅ MockComputerVision funcionando\n")

def test_mock_stt():
    """Prueba MockSpeechToText"""
    print("=" * 60)
    print("🧪 Probando MockSpeechToText...")
    print("=" * 60)
    from robot_project.speech.mock_stt import MockSpeechToText

    stt = MockSpeechToText("modelo_vosk_fake")
    result = stt.listen_to_user()
    print(f"Resultado de escucha: {result}")
    print("✅ MockSpeechToText funcionando\n")

def test_mock_tts():
    """Prueba MockTextToSpeech"""
    print("=" * 60)
    print("🧪 Probando MockTextToSpeech...")
    print("=" * 60)
    from robot_project.speech.mock_tts import MockTextToSpeech

    tts = MockTextToSpeech("dispositivo_fake", "es-PE-CamilaNeural")
    tts.speak_text("Hola, soy Peri!")
    tts.deliver_message("Este es un mensaje de prueba.")
    print("✅ MockTextToSpeech funcionando\n")

def test_mock_database():
    """Prueba MockStudentDatabase"""
    print("=" * 60)
    print("🧪 Probando MockStudentDatabase...")
    print("=" * 60)
    from robot_project.database.mock_database import MockStudentDatabase

    db_config = {"host": "fake", "user": "fake", "password": "fake", "database": "fake"}
    db = MockStudentDatabase(db_config)

    # Probar conexión
    conn = db.get_connection()
    print(f"Conexión: {conn}")

    # Probar actualización
    success = db.update_student_info(12345678, 'student_points')
    print(f"Actualización exitosa: {success}")

    # Probar obtención de datos
    nombre = db.get_student_info(12345678, 'student_name')
    puntos = db.get_student_info(12345678, 'student_points')
    print(f"Estudiante: {nombre}, Puntos: {puntos}")

    # Probar código inválido
    success = db.update_student_info(99999999, 'student_points')
    print(f"Código inválido debe fallar: {not success}")

    print("✅ MockStudentDatabase funcionando\n")

def test_mock_llm():
    """Prueba MockLargeLanguageModel"""
    print("=" * 60)
    print("🧪 Probando MockLargeLanguageModel...")
    print("=" * 60)
    from robot_project.llm.mock_llm import MockLargeLanguageModel

    llm = MockLargeLanguageModel("fake_key", "fake_base", "fake_model")

    # Pregunta sobre reciclaje
    respuesta1 = llm.ask_llm("¿Por qué es importante reciclar?")
    print(f"Respuesta 1: {respuesta1}\n")

    # Pregunta general
    respuesta2 = llm.ask_llm("¿Cómo estás?")
    print(f"Respuesta 2: {respuesta2}\n")

    # Respuesta específica
    respuesta3 = llm.generate_recycling_response("papel")
    print(f"Respuesta 3: {respuesta3}")

    print("✅ MockLargeLanguageModel funcionando\n")

def main():
    print("\n" + "=" * 60)
    print("🚀 INICIANDO PRUEBAS DE COMPONENTES MOCK")
    print("=" * 60 + "\n")

    try:
        # Verificar que estamos en modo mock
        is_mock = test_environment()
        if not is_mock:
            print("⚠️  Advertencia: No estás en modo mock")
            print("   Las pruebas pueden requerir hardware real\n")

        # Ejecutar todas las pruebas
        test_mock_serial()
        test_mock_vision()
        test_mock_stt()
        test_mock_tts()
        test_mock_database()
        test_mock_llm()

        print("=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\n🎉 ¡Todos los componentes mock están funcionando!")
        print("🚀 Ahora puedes ejecutar: python main.py\n")

        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR EN LAS PRUEBAS")
        print("=" * 60)
        print(f"\n{type(e).__name__}: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
