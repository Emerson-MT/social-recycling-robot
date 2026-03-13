#!/bin/bash

# Configuración
MAC_ADDR="F5:4E:FD:30:F8:61"
PYTHON_MAIN="main.py" 
VENV_PATH="./peri_venv/bin/activate"

echo "---------------------------------------"
echo "🤖 Iniciando sistema de audio MiniPeri"
echo "---------------------------------------"

# 1. Forzar reinicio del stack de Bluetooth si está ocupado
echo "🔄 Limpiando estado de Bluetooth..."
bluetoothctl disconnect $MAC_ADDR > /dev/null 2>&1
sleep 1
bluetoothctl power off
sleep 1
bluetoothctl power on
sleep 2

# 2. Intentar conexión
echo "🔗 Conectando al Tronsmart T7 Mini..."
bluetoothctl trust $MAC_ADDR
bluetoothctl connect $MAC_ADDR

sleep 3

# 3. Verificar conexión
if bluetoothctl info $MAC_ADDR | grep -q "Connected: yes"; then
    echo "✅ Conexión establecida."
    
    # Ajustar volumen
    pactl set-sink-volume @DEFAULT_SINK@ 80%
    
    # 4. Activar VENV automáticamente si existe
    if [ -f "$VENV_PATH" ]; then
        echo "🐍 Activando entorno virtual..."
        source $VENV_PATH
    fi

    echo "🚀 Lanzando MiniPeri..."
    python3 $PYTHON_MAIN
else
    echo "❌ Error: 'br-connection-busy' o tiempo de espera agotado."
    echo "💡 Consejo: Asegúrate de que tu celular no esté conectado al parlante."
fi
