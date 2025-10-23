#!/bin/bash
# Script de configuración para desarrollo local (PC)

echo "=========================================="
echo "Configuración de Entorno de Desarrollo"
echo "=========================================="
echo ""

# Verificar si python3-venv está instalado
if ! dpkg -l | grep -q python3.*-venv; then
    echo "⚠️  python3-venv no está instalado"
    echo "Ejecuta: sudo apt install python3.12-venv"
    echo ""
    read -p "¿Quieres instalarlo ahora? (s/n): " respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        sudo apt install python3.12-venv
    else
        echo "❌ Instalación cancelada. Instala python3-venv manualmente."
        exit 1
    fi
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias de desarrollo
echo "📦 Instalando dependencias de desarrollo..."
pip install -r requirements-dev.txt

echo ""
echo "=========================================="
echo "✅ Configuración completada"
echo "=========================================="
echo ""
echo "Para activar el entorno virtual, ejecuta:"
echo "  source venv/bin/activate"
echo ""
echo "Para ejecutar el programa:"
echo "  python main.py"
echo ""
echo "Para desactivar el entorno virtual:"
echo "  deactivate"
echo ""
