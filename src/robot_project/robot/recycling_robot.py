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
                self.test_conversacion()
            case _:
                print("Número de test inválido.")

    def run_main_program(self):
        """Ejecuta el programa principal con el sistema seleccionado (niveles o legacy)"""
        fsm = RecyclingFSM(self)
        fsm.run()
