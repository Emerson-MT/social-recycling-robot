import time
import random

class MockSerialConnection:
    """Simulación de conexión serial para desarrollo sin hardware"""

    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_connected = False
        self.last_command = None
        print(f"🔧 [MOCK] Conexión serial simulada en {port}")

    def connect(self):
        """Simula la conexión"""
        print(f"🔧 [MOCK] Conectando a {self.port}...")
        time.sleep(0.5)
        self.is_connected = True
        print("✅ [MOCK] Conectado exitosamente")

    def disconnect(self):
        """Simula la desconexión"""
        self.is_connected = False
        print("🔧 [MOCK] Desconectado")

    def send(self, data):
        """Simula el envío de datos"""
        self.last_command = data.strip()
        print(f"📤 [MOCK] Enviando: {data.strip()}")

    def wait_for_message(self, prefix, validator=None, value_type=int):
        """Simula la espera de mensajes del Arduino"""
        print(f"📥 [MOCK] Esperando mensaje con prefijo: {prefix}")
        time.sleep(0.5)  # Simula latencia

        # Simula respuestas según el tipo de mensaje
        if prefix == "LLENO:":
            # Simula que el tacho nunca está lleno en desarrollo
            valor = 0
            print(f"📥 [MOCK] Recibido: LLENO:{valor}")
            return valor

        elif prefix == "POS:":
            # Simula que el residuo siempre está en posición
            valor = 1
            print(f"📥 [MOCK] Recibido: POS:{valor}")
            return valor

        elif prefix == "LISTO:":
            # Simula que la operación se completó
            valor = 1
            print(f"📥 [MOCK] Recibido: LISTO:{valor}")
            return valor

        elif prefix == "BOTON_RES:":
            # Simula presión de botón (valores 0-3)
            valor = random.randint(0, 3)
            print(f"📥 [MOCK] Recibido: BOTON_RES:{valor}")
            return valor

        else:
            # Respuesta genérica
            valor = 1
            print(f"📥 [MOCK] Recibido: {prefix}{valor}")
            return valor
