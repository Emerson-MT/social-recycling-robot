#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA - RASPBERRY PI 5
Recibe y procesa datos de los sensores desde ESP32

Requisitos:
    pip install pyserial

Uso:
    python3 raspberry_sensor_test.py
"""

import serial
import json
import time
from datetime import datetime
import sys

# =============== CONFIGURACIÓN ===============
SERIAL_PORT = '/dev/ttyUSB0'  # Ajustar según tu configuración
BAUD_RATE = 9600
TIMEOUT = 1

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# =============== CLASE PRINCIPAL ===============
class SensorMonitor:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = False
        
    def connect(self):
        """Conecta con el ESP32"""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=TIMEOUT)
            time.sleep(2)  # Esperar a que se estabilice la conexión
            print(f"{Colors.OKGREEN}✓ Conectado a {self.port} @ {self.baud_rate} baud{Colors.ENDC}")
            return True
        except serial.SerialException as e:
            print(f"{Colors.FAIL}✗ Error al conectar: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}Verifica que el puerto sea correcto y que tengas permisos.{Colors.ENDC}")
            print(f"{Colors.WARNING}Prueba: sudo usermod -a -G dialout $USER{Colors.ENDC}")
            return False
    
    def parse_json_line(self, line):
        """Intenta parsear una línea JSON"""
        try:
            data = json.loads(line)
            return data
        except json.JSONDecodeError:
            return None
    
    def process_data(self, data):
        """Procesa y muestra los datos recibidos"""
        if not data:
            return
        
        timestamp = data.get('timestamp', 0)
        sensors = data.get('sensors', {})
        detections = data.get('detections', {})
        
        # Obtener valores
        user1 = sensors.get('user1', -1)
        user2 = sensors.get('user2', -1)
        waste = sensors.get('waste', -1)
        user_detected = detections.get('user', False)
        waste_detected = detections.get('waste', False)
        
        # Imprimir resumen
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Timestamp:{Colors.ENDC} {timestamp} ms ({timestamp/1000:.2f} s)")
        print(f"{Colors.HEADER}{'-'*60}{Colors.ENDC}")
        
        # Distancias
        print(f"{Colors.OKBLUE}📏 DISTANCIAS:{Colors.ENDC}")
        print(f"   Sensor Usuario 1: {self.format_distance(user1)}")
        print(f"   Sensor Usuario 2: {self.format_distance(user2)}")
        print(f"   Sensor Residuo:   {self.format_distance(waste)}")
        
        # Detecciones
        print(f"{Colors.OKCYAN}🔍 DETECCIONES:{Colors.ENDC}")
        user_status = f"{Colors.OKGREEN}✓ DETECTADO{Colors.ENDC}" if user_detected else f"{Colors.FAIL}✗ NO DETECTADO{Colors.ENDC}"
        waste_status = f"{Colors.OKGREEN}✓ DETECTADO{Colors.ENDC}" if waste_detected else f"{Colors.FAIL}✗ NO DETECTADO{Colors.ENDC}"
        print(f"   Usuario:  {user_status}")
        print(f"   Residuo:  {waste_status}")
        
        # Alertas
        if user_detected:
            print(f"\n{Colors.WARNING}🔔 ALERTA: Usuario presente (>2s acumulados){Colors.ENDC}")
        
        if waste_detected:
            print(f"\n{Colors.WARNING}🗑️  ALERTA: Residuo en posición (<200mm){Colors.ENDC}")
    
    def format_distance(self, dist):
        """Formatea la distancia para impresión"""
        if dist < 0:
            return f"{Colors.FAIL}---- mm (fuera de rango){Colors.ENDC}"
        elif dist < 200:
            return f"{Colors.WARNING}{dist} mm (CERCA){Colors.ENDC}"
        elif dist < 1000:
            return f"{Colors.OKGREEN}{dist} mm{Colors.ENDC}"
        else:
            return f"{Colors.OKBLUE}{dist} mm{Colors.ENDC}"
    
    def monitor(self):
        """Loop principal de monitoreo"""
        if not self.ser:
            print(f"{Colors.FAIL}No hay conexión serial{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}INICIANDO MONITOREO DE SENSORES{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.WARNING}Presiona Ctrl+C para detener{Colors.ENDC}\n")
        
        self.running = True
        json_buffer = ""
        
        try:
            while self.running:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    # Si la línea empieza con '{', es JSON
                    if line.startswith('{'):
                        json_buffer = line
                        
                        # Intentar parsear
                        data = self.parse_json_line(json_buffer)
                        if data:
                            self.process_data(data)
                            json_buffer = ""
                    else:
                        # Imprimir líneas de texto normal (debug del ESP32)
                        print(f"{Colors.OKCYAN}[ESP32] {line}{Colors.ENDC}")
                
                time.sleep(0.01)  # Pequeño delay
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Deteniendo monitor...{Colors.ENDC}")
            self.running = False
        
        except Exception as e:
            print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cierra la conexión serial"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"{Colors.OKGREEN}✓ Conexión cerrada{Colors.ENDC}")

# =============== FUNCIÓN PRINCIPAL ===============
def main():
    print(f"{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     MONITOR DE SENSORES - RASPBERRY PI 5              ║")
    print("║     Recepción de datos desde ESP32                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Permitir especificar puerto por argumento
    port = SERIAL_PORT
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print(f"Puerto configurado: {port}")
    print(f"Baud rate: {BAUD_RATE}")
    print(f"\n{Colors.WARNING}Si el puerto es incorrecto, pásalo como argumento:{Colors.ENDC}")
    print(f"{Colors.WARNING}  python3 raspberry_sensor_test.py /dev/ttyACM0{Colors.ENDC}\n")
    
    # Crear monitor y conectar
    monitor = SensorMonitor(port, BAUD_RATE)
    
    if monitor.connect():
        monitor.monitor()
    else:
        print(f"\n{Colors.FAIL}No se pudo establecer la conexión.{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Puertos disponibles:{Colors.ENDC}")
        print(f"  - /dev/ttyUSB0 (adaptador USB-Serial)")
        print(f"  - /dev/ttyACM0 (conexión USB directa)")
        sys.exit(1)

if __name__ == "__main__":
    main()
