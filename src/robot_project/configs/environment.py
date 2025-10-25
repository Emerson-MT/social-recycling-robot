import platform
import os

def is_raspberry_pi():
    """Detecta si el código se está ejecutando en una Raspberry Pi"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return 'Raspberry Pi' in model
    except:
        return False

def get_environment():
    """Devuelve 'raspberry_pi' o 'development'"""
    return 'raspberry_pi' if is_raspberry_pi() else 'development'

def is_mock_mode():
    """Verifica si se debe usar modo mock (desarrollo local)"""
    # Puedes forzar el modo mock con una variable de entorno
    if os.getenv('ROBOT_MODE', '').lower() in ['sim', 'mock']:
        return True
    elif os.getenv('ROBOT_MODE', '') == 'real':
        return False
    return not is_raspberry_pi()
