# Guía de Desarrollo Local

Este documento explica cómo ejecutar el código del robot en tu PC local sin necesidad del hardware de la Raspberry Pi 5.

## Instalación rápida

### Opción 1: Script automático (recomendado)

```bash
./setup_dev.sh
```

Este script instalará:
- `python3-venv` (si no está instalado)
- Creará el entorno virtual `venv/`
- Instalará solo las dependencias necesarias para desarrollo

### Opción 2: Manual

```bash
# 1. Instalar python3-venv
sudo apt install python3.12-venv

# 2. Crear el entorno virtual
python3 -m venv venv

# 3. Activar el entorno virtual
source venv/bin/activate

# 4. Actualizar pip
pip install --upgrade pip

# 5. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

## ¿Cómo funciona?

El sistema detecta automáticamente si se está ejecutando en una Raspberry Pi o en una PC de desarrollo. Cuando se ejecuta en modo desarrollo (PC local), usa **componentes mock** que simulan el hardware:

### Componentes simulados en modo desarrollo:

- **SerialConnection** → `MockSerialConnection`: Simula la comunicación con Arduino
- **ComputerVision** → `MockComputerVision`: Simula la clasificación de residuos sin cámara
- **SpeechToText** → `MockSpeechToText`: Desactiva el micrófono (solo entrada de consola)
- **TextToSpeech** → `MockTextToSpeech`: Imprime texto en lugar de generar audio
- **StudentDatabase** → `MockStudentDatabase`: Base de datos en memoria (sin MySQL)
- **LargeLanguageModel** → `MockLargeLanguageModel`: Respuestas predefinidas (sin API)
- **Audio playback**: Simula la reproducción de archivos MP3

## Uso

### Ejecutar en modo desarrollo (PC local)

Simplemente ejecuta el programa normalmente:

```bash
python main.py
```

El sistema detectará automáticamente que no estás en una Raspberry Pi y cargará los componentes mock. Verás este mensaje:

```
============================================================
🔧 MODO DESARROLLO - Usando componentes simulados
============================================================
```

### Forzar modo mock manualmente

Si por alguna razón quieres forzar el modo mock, puedes usar una variable de entorno:

```bash
export ROBOT_MODE=sim
# o
export ROBOT_MODE=mock
python main.py
```

### Ejecutar en Raspberry Pi (producción)

En la Raspberry Pi, el sistema detectará automáticamente el hardware y cargará los componentes reales:

```
============================================================
🤖 MODO PRODUCCIÓN - Usando hardware real
============================================================
```

## Comportamiento de los componentes mock

### 1. MockSerialConnection
- Simula todas las respuestas del Arduino
- `LLENO:` siempre devuelve 0 (tacho nunca lleno)
- `POS:` siempre devuelve 1 (residuo en posición)
- `LISTO:` siempre devuelve 1 (operación completada)
- `BOTON_RES:` devuelve un número aleatorio entre 0-3

### 2. MockComputerVision
- Genera clasificaciones aleatorias de residuos
- Devuelve una de las 4 clases: cartón, papel, plástico, o residuo_general
- Simula confianza entre 70% y 95%

### 3. MockSpeechToText
- No intenta acceder al micrófono
- Solo funciona la entrada por consola

### 4. MockTextToSpeech
- Imprime el texto en la consola en lugar de generar audio
- Simula el tiempo que tomaría hablar

### 5. Audio playback mock
- No requiere `sox`, `ffmpeg`, ni dispositivos ALSA
- Solo imprime el nombre del archivo que se "reproduciría"

### 6. MockStudentDatabase
- Base de datos simulada en memoria con 5 estudiantes de prueba
- Códigos válidos: 12345678, 87654321, 11111111, 22222222, 33333333
- Actualiza puntos en memoria (no persiste al reiniciar)
- No requiere MySQL ni conexión de red

### 7. MockLargeLanguageModel
- Respuestas predefinidas sobre reciclaje
- Detecta palabras clave relacionadas con medio ambiente
- No requiere API key ni conexión a internet
- Respuestas con la personalidad de Peri (lúdica y carismática)

## Ventajas

✅ **100% sin dependencias externas**: No necesitas hardware, MySQL, ni APIs
✅ **Sin internet**: Todo funciona completamente offline
✅ **Desarrollo rápido**: Prueba la lógica del programa sin esperar al hardware
✅ **Mismo código**: El código en desarrollo es el mismo que en producción
✅ **Detección automática**: No necesitas cambiar configuraciones al mover el código
✅ **Datos de prueba**: 5 estudiantes precargados para probar el sistema de recompensas

## Limitaciones

⚠️ **Entrada de consola obligatoria**: En modo mock, debes usar los comandos de teclado para interactuar
⚠️ **Datos no persisten**: Los puntos de estudiantes se resetean al reiniciar el programa
⚠️ **Respuestas LLM limitadas**: El mock tiene respuestas predefinidas, no es tan flexible como un LLM real

## Ejemplo de prueba

Ejecuta el programa y selecciona la opción 4 (Clasificación de residuo):

```bash
python main.py
```

```
--- Menú de pruebas ---
    1) Detección de proximidad
    2) Giro stepper con teclado
    3) Compuertas (servos)
    4) Clasificación de residuo (visión)
    ...

Ingrese el número de la prueba a realizar: 4
```

Verás una salida como:

```
📸 [MOCK] Clasificando residuo (esperando 3s)...
✅ [MOCK] Detectado: plástico (id 2) con confianza 0.87
Resultado final: plástico (id 2) con confianza 0.87
🔊 [MOCK] TTS: Se detectó plástico.
🤖 Robot: Se detectó plástico.
```

## Mockear componentes adicionales

Si quieres mockear la base de datos o el LLM, puedes crear archivos similares:

- `src/robot_project/database/mock_database.py`
- `src/robot_project/llm/mock_llm.py`

Y luego modificar `main.py` para cargarlos cuando `is_mock_mode()` sea True.
