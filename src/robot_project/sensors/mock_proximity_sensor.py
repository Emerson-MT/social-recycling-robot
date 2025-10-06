import time
import threading

class MockProximitySensor:
    """Mock del sensor de proximidad para detectar permanencia del usuario"""

    def __init__(self):
        self.user_present = False
        self.proximity_start_time = None

    def detect_user_presence(self, duration_seconds: float = 2.0) -> bool:
        """
        Simula la detección de permanencia del usuario.
        En modo mock, pregunta al usuario si permanece cerca.

        Args:
            duration_seconds: Tiempo mínimo requerido de permanencia

        Returns:
            bool: True si el usuario permanece, False si se retira
        """
        print(f"\n🤖 [SENSOR] ¿El usuario permanece cerca del robot por al menos {duration_seconds} segundos?")
        print("   [s] Sí, permanece")
        print("   [n] No, se retira")

        response = input("   Respuesta: ").strip().lower()

        if response == 's' or response == 'si' or response == 'sí':
            print(f"✅ Usuario permanece {duration_seconds}s cerca del robot")
            return True
        else:
            print(f"❌ Usuario se retira antes de {duration_seconds}s")
            return False

    def detect_attention(self) -> bool:
        """
        Simula la detección de atención del usuario (mirando pantalla, etc.)

        Returns:
            bool: True si el usuario está atento, False si está distraído
        """
        print("\n🤖 [SENSOR] ¿El usuario está atento (mirando la pantalla/robot)?")
        print("   [s] Sí, está atento")
        print("   [n] No, está distraído")

        response = input("   Respuesta: ").strip().lower()

        if response == 's' or response == 'si' or response == 'sí':
            print("✅ Usuario está atento")
            return True
        else:
            print("❌ Usuario está distraído")
            return False

    def measure_approach_time(self) -> float:
        """
        Simula la medición del tiempo de aproximación antes de depositar.

        Returns:
            float: Tiempo simulado en segundos
        """
        print("\n🤖 [SENSOR] ¿Cuánto tiempo estuvo el usuario cerca antes de depositar?")
        print("   [1] < 1 segundo (rápido)")
        print("   [2] 1-3 segundos (normal)")
        print("   [3] > 3 segundos (explorando)")

        response = input("   Respuesta: ").strip()

        time_map = {
            '1': 0.5,
            '2': 2.0,
            '3': 5.0
        }

        approach_time = time_map.get(response, 1.0)
        print(f"⏱️  Tiempo de aproximación simulado: {approach_time}s")
        return approach_time
