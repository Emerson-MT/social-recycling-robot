# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a social recycling robot named "Peri" that uses computer vision, speech recognition, and an LLM to interact with users and help them recycle waste correctly. The robot runs on a physical platform with Arduino integration via serial communication, manages a student rewards database, and operates through a finite state machine.

## Setup and Installation

**System dependencies:**
```bash
bash install_apt.sh
```

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**Required external resources:**
- Place STT models (Vosk) in `src/robot_project/models/`
- Place CV models (YOLO `.pt` files) in `src/robot_project/models/`
- Place audio files (`.mp3`) in `src/robot_project/audio/`

**Running the program:**
```bash
python main.py
```

## Configuration

All runtime parameters are in `src/robot_project/configs/config.json`:
- **File references**: Use filenames only (no paths). The `config_loader.py` automatically resolves paths to `models/` and `audio/` directories
- **Serial ports**: Configure Arduino connections (typically `/dev/ttyUSB0` or `/dev/ttyACM0`)
- **Audio device**: ALSA device identifier (e.g., `plughw:CARD=CODEC,DEV=0`)
- **API keys**: LLM provider credentials (currently OpenRouter with Mistral-7B)
- **Database**: MySQL connection parameters for student rewards tracking

## Architecture

### Module Structure

The codebase follows a clean modular architecture under `src/robot_project/`:

- **`robot/`**: Core robot classes
  - `general_robot.py`: Base `Robot` class with threading for dual input (voice + console), audio playback, and command queue management
  - `recycling_robot.py`: `RecyclingRobot` subclass with waste classification, Arduino communication, database integration, and `RecyclingFSM` for state machine logic

- **`speech/`**: Voice interaction
  - `stt.py`: Speech-to-text using Vosk (Spanish models)
  - `tts.py`: Text-to-speech using Edge-TTS (Spanish voices)

- **`vision/`**: Computer vision for waste classification
  - `vision.py`: YOLOv8-based waste classification with temporal voting over multiple frames

- **`llm/`**: Conversational AI
  - `llm.py`: OpenAI-compatible API integration with system prompt for Peri's personality

- **`connections/`**: Hardware communication
  - `serial_connection.py`: Arduino serial protocol for sensors, steppers, servos, and buttons

- **`database/`**: Student rewards system
  - `student_db.py`: MySQL interface for student code lookup and point updates

- **`configs/`**: Configuration management
  - `config_loader.py`: Loads JSON config and resolves file paths dynamically

### Main Program Flow

The robot operates in two modes via `main.py`:

1. **Test mode** (options 1-8): Individual component testing
2. **Main program** (option 9): Full FSM execution

The finite state machine (`RecyclingFSM`) has these states:
- `INICIO`: Voice command listening ("reciclar" or "conversar")
- `CLASIFICAR`: Computer vision waste classification
- `CONVERSACION`: LLM-based conversation (exit with "adiós")
- `ELEGIR_SEGRE`: User chooses manual ("yo") or automatic ("tú") recycling
- `RECOMPENSA`: Student code recognition and database point update

### Hardware Integration

The robot communicates with Arduino over serial using a custom protocol:
- Commands sent: `PRUEBA:N`, `RESIDUO:N`, `SEGRE_AUTO:N`, `STEP_POS:N`
- Responses parsed: `LLENO:`, `POS:`, `LISTO:`, `BOTON_RES:`

Arduino controls:
- Proximity sensors (waste detection)
- Stepper motor (trash can rotation to 4 positions: cardboard, paper, plastic, general waste)
- Servo gates (compartment doors)
- Push buttons (user manual selection)

### Voice Recognition Integration

The robot uses dual-threaded input:
- `_listen_and_queue()`: Continuous Vosk STT listening
- `console_listener()`: Keyboard command fallback for testing

Both threads populate a shared `command_queue` and set a `stop_event` when input is received.

### Speech-to-Number Conversion

For student code recognition (`text_to_number()` in `recycling_robot.py`):
- Handles numeric strings directly
- Uses `word2number_es` to convert Spanish number words ("uno dos tres" → 123)
- Returns 0 for invalid input to trigger retry

## Development Guidelines

**When modifying audio/speech:**
- Audio playback uses `sox` for ALSA devices
- TTS temporarily generates MP3, converts to WAV with `ffmpeg`, then deletes both
- MP3 audio files use `ffmpeg` → `sox` pipeline (see `Robot.play_audio()`)

**When working with vision:**
- YOLO model expects 4 classes: cartón (0), papel (1), plástico (2), residuo_general (3)
- Classification uses temporal voting over 3 seconds with 0.2 confidence threshold

**When modifying database:**
- Student codes are 8-digit integers
- Database operations should handle connection failures gracefully

**When changing FSM logic:**
- State methods must be named `state_{statename}()` (lowercase)
- State transitions modify `self.state` string
- Use `self.robot.tts.deliver_message()` for all user-facing speech

**Serial communication:**
- All serial commands end with `\n`
- Use `wait_for_message()` with validation lambdas for Arduino responses
- Arduino message format: `KEY:VALUE\n`
