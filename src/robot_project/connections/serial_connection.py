import serial
import time

class SerialConnection:
     
    def __init__(self, port='/dev/ttyACM0', baud_rate=9600, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Dar tiempo para que se establezca la conexión
            print(f"[Serial] Conectado a {self.port}")
        except serial.SerialException as e:
            print(f"[Serial Error] {e}")
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("[Serial] Conexión cerrada.")

    def send(self, data: str):
        if self.connection and self.connection.is_open:
            print(f"📤 Enviando: {data.strip()}")
            self.connection.write(data.encode())
        else:
            print("[Serial Warning] Intento de enviar sin conexión activa.")

    def read_line(self) -> str:
        if self.connection and self.connection.is_open:
            return self.connection.readline().decode().strip()
        return ""
    
    def wait_for_line(self) -> str:
        if not self.connection or not self.connection.is_open:
            return ""

        while True:
            if self.connection.in_waiting > 0:
                return self.connection.readline().decode().strip()

    def wait_for_message(self, prefix, valid_fn):
        while True:
            if self.connection.in_waiting > 0:
                msg = self.connection.readline().decode('utf-8').strip()
                if msg.startswith(prefix):
                    try:
                        value = int(msg.split(":")[1])
                        if valid_fn(value):
                            return value
                    except ValueError:
                        print("Formato incorrecto en el mensaje recibido.")
                else:
                    print(f"Mensaje no reconocido: {msg}")
