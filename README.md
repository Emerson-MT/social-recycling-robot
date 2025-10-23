Uhmm no sé xd ¿Quieres un facto? Oliver es migajero

1) Para instalar las dependencias apt, ejecutar: bash install_apt.sh
2) Para instalar las librerías python, ejecutar: pip install -r requirements.txt
3) Solo ejecuta el main y modifica los parámetros que quieras en el archivo src/robot_project/configs/config.json
4) Los archivos mp3 van en audio y los modelos en models
5) Todos los parámetros en config.json que corresponden a archivos deben consistir de solo el nombre del archivo. La ruta se obtiene en el código.

------------------------------------------------------------------------------
Branch new-mic-screen - push 1

1) Se corrigió un error en la clase SerialConnection
2) Se modificó el dispositivo de salida para que sea siempre por el ReSpeaker (cambio en config.json). Se sigue trabajando directamente con ALSA y el canal 5 del ReSpeaker por defecto.
3) Se modificó la clase TextToSpeech para ya no trabajar directamente con ALSA sino con pyaudio. Se trabaja con el canal 0 del dispositivo ReSpeaker como entrada de audio.