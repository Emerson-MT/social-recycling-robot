# Robot Social de Reciclaje - Peri 🤖♻️

Robot social interactivo que utiliza visión por computadora, reconocimiento de voz y LLM para ayudar a los usuarios a reciclar correctamente y premiar su comportamiento ecológico.

## 🚀 Inicio Rápido

### Desarrollo Local (PC)

Para probar el código en tu PC sin hardware:

```bash
# Instalación automática
./setup_dev.sh

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el programa
python main.py
```

Ver [DESARROLLO_LOCAL.md](DESARROLLO_LOCAL.md) para más detalles.

### Producción (Raspberry Pi 5)

```bash
# 1. Instalar dependencias del sistema
bash install_apt.sh

# 2. Instalar librerías de Python
pip install -r requirements.txt

# 3. Configurar config.json (ver sección Configuración)

# 4. Colocar modelos en src/robot_project/models/
# 5. Colocar archivos de audio en src/robot_project/audio/

# 6. Ejecutar
python main.py
```

## 📋 Requisitos

### Desarrollo (PC)
- Python 3.12+
- Dependencias mínimas (ver `requirements-dev.txt`)

### Producción (Raspberry Pi 5)
- Raspberry Pi 5 con Raspberry Pi OS
- Python 3.12+
- Cámara USB/CSI
- Micrófono USB
- Altavoz/Audio CODEC
- Arduino conectado vía USB
- Todas las dependencias (ver `requirements.txt`)

## ⚙️ Configuración

1. Copiar el archivo de configuración de ejemplo:
```bash
cp src/robot_project/configs/config.example.json src/robot_project/configs/config.json
```

2. Editar `config.json` con tus credenciales y configuraciones:
   - **LLM**: API key de OpenRouter u otro proveedor compatible con OpenAI
   - **Base de datos**: Credenciales MySQL
   - **Puertos serial**: Rutas de dispositivos Arduino
   - **Audio**: Identificador del dispositivo ALSA

3. Descargar modelos:
   - **STT**: [Modelo Vosk en español](https://alphacephei.com/vosk/models)
   - **CV**: Modelo YOLO entrenado para clasificación de residuos

## 🏗️ Arquitectura

```
src/robot_project/
├── robot/           # Lógica principal y FSM
├── speech/          # TTS y STT (+ mocks)
├── vision/          # Computer Vision (+ mock)
├── llm/             # Integración con LLM
├── connections/     # Comunicación serial (+ mock)
├── database/        # Gestión de estudiantes
├── configs/         # Configuración y detección de entorno
├── models/          # Modelos de IA (no en git)
└── audio/           # Archivos de audio (no en git)
```

Ver [CLAUDE.md](CLAUDE.md) para documentación detallada de la arquitectura.

## 🎮 Uso

El programa presenta un menú con 9 opciones de prueba:

1. **Detección de proximidad** - Prueba el sensor ultrasónico
2. **Giro stepper con teclado** - Control manual del motor
3. **Compuertas (servos)** - Prueba de servomotores
4. **Clasificación de residuo** - Visión por computadora
5. **Giro automático** - Movimiento automático del stepper
6. **Pulsadores** - Lectura de botones físicos
7. **Código y base de datos** - Sistema de recompensas
8. **Conversación con Peri** - Interacción con LLM
9. **Programa completo** - FSM completo del robot

## 🔄 Máquina de Estados (FSM)

El robot opera mediante una FSM con los siguientes estados:

- **INICIO**: Espera comando de voz ("reciclar" o "conversar")
- **CLASIFICAR**: Identifica el tipo de residuo con la cámara
- **CONVERSACION**: Charla sobre reciclaje con el usuario
- **ELEGIR_SEGRE**: Usuario elige segregación manual o automática
- **RECOMPENSA**: Reconoce código de estudiante y otorga puntos

## 🧪 Modo Desarrollo vs Producción

El sistema detecta automáticamente el entorno:

| Componente | Desarrollo (PC) | Producción (Raspberry Pi) |
|------------|-----------------|---------------------------|
| Serial | MockSerialConnection | SerialConnection |
| Cámara | MockComputerVision | ComputerVision |
| Micrófono | MockSpeechToText | SpeechToText |
| Altavoz | MockTextToSpeech | TextToSpeech |
| Audio | Simulado | sox + ffmpeg |

## 🤝 Contribuir

1. Clona el repositorio
2. Configura el entorno de desarrollo (`./setup_dev.sh`)
3. Crea una rama para tu feature
4. Haz tus cambios
5. Prueba en modo mock
6. Envía un pull request

## 📝 Notas Importantes

- **Seguridad**: No subas `config.json` con credenciales reales a git
- **Modelos**: Los modelos de IA son muy grandes, descárgalos por separado
- **Audio**: Los archivos MP3 tampoco se incluyen en el repositorio
- **Hardware**: El código está optimizado para Raspberry Pi 5, pero funciona en PC con mocks

## 📚 Documentación Adicional

- [CLAUDE.md](CLAUDE.md) - Guía para Claude Code
- [DESARROLLO_LOCAL.md](DESARROLLO_LOCAL.md) - Desarrollo sin hardware
- `requirements.txt` - Dependencias completas (producción)
- `requirements-dev.txt` - Dependencias mínimas (desarrollo)

## 📄 Licencia

[Incluir información de licencia aquí]

## 👥 Autores

[Incluir información de autores aquí]
