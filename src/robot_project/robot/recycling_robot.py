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
from robot_project.configs.config_loader import load_config
from robot_project.configs.environment import use_interaction_levels
from word2number_es import w2n
from typing import Dict

class RecyclingRobot(Robot):

    def __init__(self, name: str, commands: dict, audio_device: str, audio_paths: Dict[str, str], stt: SpeechToText, llm: LargeLanguageModel, tts: TextToSpeech, cv: ComputerVision, ser: SerialConnection, database: StudentDatabase):
        super().__init__(name, commands, audio_device, stt, llm, tts, cv, ser)  # Llama al constructor de Robot
        self.student_db = database
        self.audio_paths = audio_paths
        self.test = -1
    
    def is_user_there(self):
        return True
    
    def set_screen(self, state):
        pass
    
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
        valor = self.ser.wait_for_message("POS:", lambda x: x in [0, 1], int)
        
        if valor == 1:
            print("Residuo en posición")
            return True
        else:
            print("Residuo no en posición")
            return False

    def is_testing_done(self):
        return self.ser.wait_for_message("LISTO:", lambda v: v == 1)

    def get_pressed_button(self):
        return self.ser.wait_for_message("BOTON_RES:", lambda v: 0 <= v <= 3)
    
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

    def test_stepper_teclado(self):
        # Se le envía al arduino la instrucción de test
        self.ser.send(f"PRUEBA:{self.test}\n")  
        # Ingrese la posición del stepper
        step_pos = int(input("Ingrese la posición a la que mover el stepper (0 - 3): "))
        # Se envía la posición al Arduino
        self.ser.send(f"STEP_POS:{step_pos}\n")
        # Se espera confirmación de listo
        done = self.is_testing_done()
        
        if done: self.tts.deliver_message("Prueba de stepper finalizada.") 
        else: self.tts.deliver_message("Error en la prueba de stepper.")  

    def test_compuertas(self):
        print("Abriendo compuerta...")
        # Se le envía al arduino la instrucción de test
        self.ser.send(f"PRUEBA:{self.test}\n")
        
        done = self.is_testing_done()
        
        if done: self.tts.deliver_message("Prueba de abrir compuerta finalizada.")
        else: self.tts.deliver_message("Error en la prueba de abrir compuerta.")
            

    def test_vision(self):
        # We classify the waste using Computer vision
        resultado = self.classify_waste(tiempo_limite=10, confianza_minima=0.3, mostrar=True)
        # We extract details
        if resultado:

            class_id, residuo, confianza = resultado
            print(f"Resultado final: {residuo} (id {class_id}) con confianza {confianza:.2f}\n")
            self.tts.deliver_message(f"Se detectó {residuo}.")
            self.tts.deliver_message("Prueba de clasificación finalizada.")

    def test_stepper_auto(self):
        # Se le envía al arduino la instrucción de test
        self.ser.send(f"PRUEBA:{self.test}\n")
        # Se espera a que termine de moverse el stepper                
        done = self.is_testing_done()

        if done: self.tts.deliver_message("Prueba de stepper finalizada.")    
        else: self.tts.deliver_message("Error en la prueba de stepper.")
            
    def test_pulsadores(self):
        # Se le envía al arduino la instrucción de test
        self.ser.send(f"PRUEBA:{self.test}\n")
        # Se espera a realizar el Homing
        '''
        while True:
            set_homing = input("Ingrese 'H' para definir el homing del stepper en la posición actual: ")

            if set_homing.upper() == "H":
                ser.write("H\n".encode())
                deliver_message("Homing realizado! Ahora puedes usar los botones.")
                break
            else:
                deliver_message("Comando incorrecto. Intenta de nuevo.")
        '''
        # Se espera a obtener el botón pulsado
        pressed_button = self.get_pressed_button()
        # Se comunica al usuario
        self.tts.deliver_message(f"El pulsador presionado fue el {pressed_button}.\n")

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
        if use_interaction_levels():
            print("=" * 60)
            print("🌟 MODO NIVELES DE INTERACCIÓN ACTIVADO")
            print("=" * 60)
            from robot_project.robot.interaction_levels_fsm import InteractionLevelsFSM
            fsm = InteractionLevelsFSM(self)
            fsm.run()
        else:
            print("=" * 60)
            print("📋 MODO LEGACY ACTIVADO")
            print("=" * 60)
            fsm = RecyclingFSM(self)
            fsm.run()

class RecyclingFSM:

    def __init__(self, robot: RecyclingRobot):
        self.robot = robot
        self.state = "INICIO"
        self.class_id = None
        self.residuo = None
        self.confianza = None

    def run(self):
        try:
            while True:
                getattr(self, f"state_{self.state.lower()}")()
        except KeyboardInterrupt:
            print("Interrupción del programa principal")

    def state_inicio(self):
        # escuchar comando de voz inicial
        self.robot.play_audio(self.robot.audio_paths["start_audio_path"])
        self.robot.tts.deliver_message("Hola, soy Peri. Reciclemos juntos!.")
        while True:

            self.robot.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
            command = self.robot.get_response() # Se espera el comando en el queue

            # Cambia el estado según el comando
            if command.lower() == "reciclar" or command.lower() == "recicla esto" or command.lower() == "por favor recicla esto" or command.lower() == "recicla esto por favor" or command.lower() == "ayúdame con esto" or command.lower() == "ayúdame a reciclar esto":
                self.state = "CLASIFICAR"
                self.robot.tts.deliver_message("Genial! Sigue las instrucciones para empezar.")
                break
            elif command.lower() == "conversar":
                self.state = "CONVERSACION"
                self.robot.tts.deliver_message("Hablemos! Puedes decir adiós cuando quieras terminar.")
                break
            else:
                self.robot.tts.deliver_message("No te entendí, ¿puedes repetirlo?")

    def state_clasificar(self):
        # clasifica el residuo
        resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)
        # Se obtienen datos relevantes del resultado
        if resultado:                      
            # Se desglosa el resultado
            self.class_id, self.residuo, self.confianza = resultado
            # Comunicación con el usuario
            print(f"Resultado final: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}\n")
            self.robot.tts.deliver_message(f"Se detectó {self.residuo}.")
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
            # Se le envía al arduino la instrucción de test
            time.sleep(0.5)
            # Se revisa si el tacho está lleno o no
            #is_full = is_trash_can_full(ser, class_id)                                
            # Si hay espacio en el tacho, se podrá hacer la segregación
            is_full = False
            if is_full == False:
                self.robot.tts.deliver_message("¿Quieres que lo recicle yo o prefieres hacerlo tú para ganar una recompensa?")
                # Pasamos al siguiente state
                self.state = "ELEGIR_SEGRE"
            elif is_full == True:
                self.robot.tts.deliver_message(f"Lo lamento, mi contenedor para {self.residuo} se encuentra lleno. Por favor toma el residuo y colócalo en otro tacho. Gracias por ayudar a reciclar!")
                # Reiniciamos todo
                self.state = "INICIO"
        else:  
            print("No se detectó ningún residuo válido.")
        
    def state_conversacion(self):
        # ciclo de conversación
        self.robot.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
        command = self.robot.get_response() # Se espera el comando en el queue
        
        if command:
            print(f"🗣️ texto reconocido: {command}")
            if command.lower() == "adios" or command.lower() == "adiós":
                self.robot.tts.deliver_message("Me gustó hablar contigo. ¡Hasta pronto!") 
                self.state = "INICIO"
                time.sleep(5)
            else:
                respuesta = self.robot.llm.ask_llm(command)
                self.robot.tts.deliver_message(respuesta)
        else:
            self.robot.tts.deliver_message("No entendí eso. ¿Puedes repetirlo?")
        
    def state_elegir_segre(self):
        # "yo" o "tú"
        self.robot.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
        command = self.robot.get_response() # Se espera el comando en el queue
        
        if command.lower() == "yo" or command.lower() == "yo lo reciclo" or command.lower() == "yo lo hago" or command.lower() == "yo me encargo": # El usuario quiere reciclar por si mismo
            self.robot.tts.deliver_message("Presiona el botón correcto según el tipo de residuo.")
            print("Esperando que usuario presione botón:\n")
            # Se espera del Arduino el botón presionado por el usuario
            self.robot.ser.send(f"SEGRE_AUTO:0\n")
            # Se le envía al arduino la instrucción de test
            time.sleep(0.5)
            pred_residuo = self.robot.get_pressed_button()                         
            # Se compara el residuo real con la opción presionada            
            if  pred_residuo == self.class_id:
                # El Arduino ya hizo esta comparación y realiza la segregación si son iguales
                self.state = "RECOMPENSA"       
            else:
                self.robot.play_audio(self.robot.audio_paths["lose_audio_path"])
                self.robot.tts.deliver_message("Uy, ese no era. Mejor suerte la próxima vez!")
                self.state = "INICIO"

            time.sleep(5)
            
        elif command.lower() == "tu" or command.lower() == "tú" or command.lower() == "hazlo tu" or command.lower() == "hazlo tú": # El usuario quiere que el robot se encargue
            # Se le indica al Arduino hacer la segregción automática, no esperar al usuario
            self.robot.tts.deliver_message("Listo! Yo me encargo.")
            #deliver_message("Ah hábil te crees conchatumare.")
            self.robot.ser.send(f"SEGRE_AUTO:1\n")
            self.robot.tts.deliver_message("Gracias por reciclar! Hasta pronto!")
            self.state = "INICIO"
            time.sleep(5)
        else:
            self.robot.tts.deliver_message("No te entendí, ¿puedes repetirlo?")

    def state_recompensa(self):

        self.robot.play_audio(self.robot.audio_paths["win_audio_path"])
        self.robot.tts.deliver_message("Bien hecho! Ganaste una recompensa. ¿Cuál es tu código?")
        student_code = 0

        while True:
            # escucha código, actualiza base de datos
            self.robot.start_listening_threads() # Se inician los threads que esperan el comando de voz o por consola
            text = self.robot.get_response() # Se espera el comando en el queue
            print(f"text reconocido: {text}\n")
            student_code = self.robot.text_to_number(text)

            if student_code != 0:
                
                # Se informa del código detectado
                print(f"Código interpretado: {student_code}\n")
                self.robot.tts.deliver_message(f"Escuché {text}")
                # Se establece conexión con la base de datos
                conexion = self.robot.student_db.get_connection()
                # Se hace la búsqueda de datos de estudiante con su código
                success = self.robot.student_db.update_student_info(student_code, 'student_points')
                # Si se realizó con éxito la actualización, se sale del bucle
                if success:
                    first_name = self.robot.student_db.get_student_info(student_code, 'student_name').split()[0]
                    student_points = self.robot.student_db.get_student_info(student_code, 'student_points')
                    self.robot.tts.deliver_message(f"Hola {first_name}! Gracias por ayudar a reciclar. Tus puntos ahora son de {student_points}. Hasta pronto!")
                    self.state = "INICIO"
                    break
                else:
                    self.robot.tts.deliver_message("Lo siento, no encontré ese código de estudiante. Por favor intenta de nuevo.")
