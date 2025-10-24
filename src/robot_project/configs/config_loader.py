import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
AUDIO_DIR = Path(__file__).resolve().parent.parent / "audio"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Resolve file paths
    config["stt"]["model_path"] = str(MODELS_DIR / config["stt"]["model_file"])
    #config["cv"]["model_path"] = str(MODELS_DIR / config["cv"]["model_file"])
    config["audio_files"]["start_audio_path"] = str(AUDIO_DIR / config["audio_files"]["start_audio_file"])
    config["audio_files"]["win_audio_path"] = str(AUDIO_DIR / config["audio_files"]["win_audio_file"])
    config["audio_files"]["lose_audio_path"] = str(AUDIO_DIR / config["audio_files"]["lose_audio_file"])

    return config

