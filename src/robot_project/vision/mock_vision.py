import time
import random

class MockComputerVision:
    """Simulación de Computer Vision para desarrollo sin cámara"""

    def __init__(self, model_path):
        self.cv_model = None
        print("🔧 [MOCK] Modelo de Computer Vision simulado")
        print(f"🔧 [MOCK] Ruta del modelo: {model_path}")

    def load_cv_model(self, path):
        """Simula la carga del modelo"""
        print("⏳ [MOCK] Cargando modelo de Computer Vision...")
        time.sleep(1)
        self.cv_model = "mock_model"
        print("✅ [MOCK] Modelo cargado")

    def classify(self, tiempo_limite=3, confianza_minima=0.2):
        """Simula la clasificación de residuos"""
        print(f"📸 [MOCK] Clasificando residuo (esperando {tiempo_limite}s)...")
        time.sleep(2)

        # Clases disponibles: 0=cartón, 1=papel, 2=plástico, 3=residuo_general
        clases = [
            (0, "cartón", random.uniform(0.7, 0.95)),
            (1, "papel", random.uniform(0.7, 0.95)),
            (2, "plástico", random.uniform(0.7, 0.95)),
            (3, "residuo_general", random.uniform(0.7, 0.95))
        ]

        # Selecciona una clase aleatoria
        class_id, class_name, confidence = random.choice(clases)

        print(f"✅ [MOCK] Detectado: {class_name} (id {class_id}) con confianza {confidence:.2f}")

        return (class_id, class_name, confidence)
