import queue
import subprocess
import os
import threading
import time
from robot_project.llm import LargeLanguageModel
from robot_project.speech import TextToSpeech, SpeechToText
from robot_project.vision import ComputerVision
from robot_project.connections import SerialConnection
from robot_project.robot import Robot
from robot_project.database import StudentDatabase
from robot_project.display import Display
from robot_project.configs.config_loader import load_config
from robot_project.fsm.recycling_fsm import RecyclingFSM
from word2number_es import w2n
from typing import Dict

class RecyclingRobot(Robot):

    def __init__(self, name: str, commands: dict, audio_device: str, audio_paths: Dict[str, str],
                  stt: SpeechToText, llm: LargeLanguageModel, tts: TextToSpeech, 
                  cv: ComputerVision, ser: SerialConnection, database: StudentDatabase,
                  display: Display
                  ):
        super().__init__(name, commands, audio_device, stt, llm, tts, cv, ser, display)  # Llama al constructor de Robot
        self.student_db = database
        self.audio_paths = audio_paths
        self.test = -1
    
    def is_user_there(self):
        valor = self.ser.wait_for_message("USUARIO:", lambda x: x in [0, 1])
        
        if valor == 1:
            print("Usuario detectado")
            return True
        else:
            print("No hay usuario")
            return False
    
    def set_test_num(self, test_num):
        self.test = test_num

    def classify_waste(self, *args, **kwargs):
        return self.cv.classify(*args, **kwargs)
    
    def is_trash_can_full(self, class_id):
        self.ser.send(f"RESIDUO:{class_id}\n")
        
        valor = self.ser.wait_for_message("LLENO:", lambda x: x in [0, 1])

        if valor == 0:
            print("El tacho cuenta con espacio")
        else:
            print("El tacho no cuenta con espacio")

        return True if valor == 1 else False
    
    def is_waste_in_position(self):
        valor = self.ser.wait_for_message("RES_EN_POS:", lambda x: x in [0, 1])
        
        if valor == 1:
            print("Residuo en posición")
            return True
        else:
            print("Residuo no en posición")
            return False

    def is_testing_done(self):
        return self.ser.wait_for_message("LISTO:", lambda v: v == 1)
    
    def text_to_number(self, text):

        if text.replace(" ", "").isdigit():
            # Entrada de consola ya en formato numérico
            codigo = int(text)
            return codigo
        else:
            palabras = text.split()
            codigo = 0
            ex = 7
            try:
                for palabra in palabras:
                    codigo += w2n.word_to_num(palabra)*pow(10, ex)
                    ex -= 1
                return codigo
            except Exception as e:
                return 0
    
    # Pruebas de funcionamiento
    def test_proximidad(self):
        # We tell Arduino the test to perform
        self.ser.send(f"PRUEBA:{self.test}\n")    
        # We wait for the waste to be in position within the desired time lapse
        in_pos = self.is_waste_in_position()
        
        if in_pos: self.tts.deliver_message("Residuo detectado. Prueba finalizada")
        else: self.tts.deliver_message("Residuo no detectado en el tiempo indicado. Prueba finalizada") 
            
    def test_vision(self):
        # We classify the waste using Computer vision
        resultado = self.classify_waste(tiempo_limite=10, confianza_minima=0.3, mostrar=True)
        # We extract details
        if resultado:

            class_id, residuo, confianza = resultado
            print(f"Resultado final: {residuo} (id {class_id}) con confianza {confianza:.2f}\n")
            self.tts.deliver_message(f"Se detectó {residuo}.")
            self.tts.deliver_message("Prueba de clasificación finalizada.")

    def test_codigo_y_recompensa(self):
        self.tts.speak_text("Ingrese el residuo detectado")
        class_id = int(input("Ingrese el residuo detectado: "))
        self.tts.speak_text("Ahora ingrese el contenedor al que corresponde")
        pred_residuo = int(input("Ingrese el contenedor al que corresponde: "))

        if  pred_residuo == class_id:
            # El Arduino ya hizo esta comparación y realiza la segregación si son iguales
            self.tts.deliver_message("Muy bien! Te ganaste una recompensa. Por favor díctame tu código.")
            student_code = 0

            while True:

                # Se espera hasta terminar de hablar antes de volver a escuchar
                self.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
                text = self.get_response() # Se espera el comando en el queue
                print(type(text))
                print(f"text reconocido: {text}\n")
                student_code = self.text_to_number(text)
                print(type(student_code))

                if student_code != 0:
                    
                    # Se informa del código detectado
                    print(f"Código interpretado: {student_code}\n")
                    #deliver_message(f"Escuché {text}")
                    # Se establece conexión con la base de datos
                    conexion = self.student_db.get_connection()
                    # Se hace la búsqueda de datos de estudiante con su código
                    success = self.student_db.update_student_info(student_code, 'student_points')
                    # Si se realizó con éxito la actualización, se sale del bucle
                    if success:
                        first_name = self.student_db.get_student_info(student_code, 'student_name').split()[0]
                        student_points = self.student_db.get_student_info(student_code, 'student_points')
                        self.tts.deliver_message(f"Hola {first_name}! Gracias por ayudar a reciclar. Tus puntos ahora son de {student_points}. Hasta pronto!")
                        break    
                    else:
                        self.tts.deliver_message("Lo siento, no encontré ese código. Por favor intenta de nuevo.")
        else:
            self.tts.deliver_message("Lo siento, ese no es el contenedor correcto. Mejor suerte para la próxima!")

    def test_conversacion(self):
        while True:
            self.tts.deliver_message("Se eligió coversar. Cuentame, estoy aquí para escucharte. Puedes decirme adiós cuando ya no quieras hablar")
            self.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
            command = self.get_response() # Se espera el comando en el queue

            if command:
                print(f"🗣️  texto reconocido: {command}")
                if command.lower() == "adios" or command.lower() == "adiós":
                    self.tts.deliver_message("Un gusto conversar contigo. Hasta pronto!")
                    break 
                else:
                    respuesta = self.llm.ask_llm(command)
                    self.tts.deliver_message(respuesta)
            else:
                self.tts.deliver_message("No se entendió. Intenta de nuevo.\n")
                
    def test_djperigro_mode(self):
        """Modo DJPERIGRO: Muestra botón DJPERIGRO, ruleta musical y reproduce la canción seleccionada"""
        from pathlib import Path
        
        print("\n" + "="*60)
        print("🎧 INICIANDO MODO DJPERIGRO")
        print("="*60)
        print("Mostrando botón DJPERIGRO en pantalla...\n")
        
        # Mostrar botón DJPERIGRO y esperar interacción
        button_pressed = self.display.show_djperigro_button()
        
        if button_pressed:
            print("✨ ¡BOTÓN DJPERIGRO PRESIONADO!")
            print("🎲 Girando la ruleta musical...\n")
            
            # Directorio base de audio
            audio_base = Path(__file__).resolve().parent / "audio"
            
            # Buscar directorio de audio en múltiples ubicaciones
            possible_audio_dirs = [
                audio_base,
                Path("src/robot_project/audio"),
                Path("audio"),
                Path.cwd() / "Audio",
                Path(__file__).parent / "audio"
            ]
            
            audio_dir = None
            for path in possible_audio_dirs:
                if path.exists() and path.is_dir():
                    audio_dir = path
                    print(f"📁 Directorio de audio encontrado: {audio_dir}")
                    break
            
            if not audio_dir:
                print("⚠️ No se encontró el directorio de audio")
                print("Ubicaciones buscadas:")
                for path in possible_audio_dirs:
                    print(f"  - {path}")
                print("❌ Modo DJPERIGRO cancelado\n")
                return
            
            # Buscar archivos MP3 en el directorio de audio
            # Lista de archivos a excluir (efectos de sonido, no canciones)
            excluded_files = [
                "losing_sound-effect",
                "starting_sound-effect", 
                "winning_sound-effect"
            ]
            
            songs_data = []
            for file in audio_dir.glob("*.mp3"):
                song_name = file.stem  # Nombre sin extensión
                
                # Excluir archivos de efectos de sonido
                if song_name in excluded_files:
                    continue
                
                songs_data.append({
                    'name': song_name,
                    'path': str(file)
                })
            
            if not songs_data:
                print("⚠️ No se encontraron canciones MP3 en el directorio de audio")
                print(f"Directorio: {audio_dir}")
                print("❌ Modo DJPERIGRO cancelado\n")
                return
            
            # Extraer solo los nombres para la ruleta
            song_names = [song['name'] for song in songs_data]
            
            print(f"🎵 Canciones encontradas: {len(song_names)}")
            for song in song_names:
                print(f"  - {song}")
            print(f"⏭️  Archivos excluidos: {', '.join(excluded_files)}\n")
            
            # Mostrar ruleta y obtener canción seleccionada
            selected_song_name = self.display.show_song_roulette(song_names, duration=3.0)
            
            # Buscar la ruta de la canción seleccionada
            selected_song_path = None
            for song in songs_data:
                if song['name'] == selected_song_name:
                    selected_song_path = song['path']
                    break
            
            if selected_song_path:
                print(f"\n🎊 Canción seleccionada: {selected_song_name}")
                print(f"🎵 Reproduciendo...\n")
                
                try:
                    # Reproducir audio usando el sistema del robot
                    self.play_audio(selected_song_path)
                    print("✅ Reproducción completada")
                except Exception as e:
                    print(f"⚠️ Error al reproducir audio: {e}")
                    print("Intentando con pygame.mixer...")
                    
                    # Fallback: usar pygame mixer directamente
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load(selected_song_path)
                        pygame.mixer.music.play()
                        
                        # Esperar a que termine la canción
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        
                        print("✅ Reproducción completada (pygame)")
                    except Exception as e2:
                        print(f"❌ Error con pygame mixer: {e2}")
            else:
                print(f"❌ Error: No se pudo encontrar la ruta de la canción '{selected_song_name}'")
        else:
            print("❌ Modo DJPERIGRO cancelado\n")
        else:
            print("❌ Modo Golden cancelado\n")

    def run_test(self, test: int):
        match test:
            case 1:
                self.test_proximidad()
            case 2:
                self.test_stepper_teclado()
            case 3:
                self.test_compuertas()
            case 4:
                self.test_vision()
            case 5:
                self.test_stepper_auto()
            case 6:
                self.test_pulsadores()
            case 7:
                self.test_codigo_y_recompensa()
            case 8:
                self.test_golden_mode()
            case _:
                print("Número de test inválido.")

    def run_main_program(self):
        """Ejecuta el programa principal con el sistema seleccionado (niveles o legacy)"""
        fsm = RecyclingFSM(self)
        fsm.run()




