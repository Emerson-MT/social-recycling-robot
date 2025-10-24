import time
from typing import Optional, Dict
from robot_project.sensors import MockProximitySensor
from robot_project.display import MockDisplay
from robot_project.gamification import QuizSystem, AchievementSystem
from robot_project.analytics import ImpactCalculator
from robot_project.configs.config_loader import load_config

class InteractionLevelsFSM:
    """
    Máquina de estados finitos para niveles de interacción progresiva.
    """

    def __init__(self, robot: RecyclingRobot):
        self.robot = robot
        self.config = load_config()
        self.levels_config = self.config.get("interaction_levels", {})

        # Componentes del sistema de niveles
        self.proximity_sensor = MockProximitySensor()
        self.display = MockDisplay()

        # Estado del sistema
        self.state = "HIBERNACION"
        self.class_id = None
        self.residuo = None
        self.confianza = None

    def run(self):
        """Ejecuta la FSM de niveles de interacción"""
        try:
            while True:
                getattr(self, f"state_{self.state.lower()}")()
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del programa de niveles")

    def state_hibernacion(self):
        """Estado hibernacion: Espera a que haya un usuario para entrar al estado 'despertando'
        o que haya un residuo en posición para continuar al estado 'clasificar_1'. En este estado
        se supone que una persona pasó demasiado rápido como para interactuar y solo se segrega."""

        self.robot.ser.send(f"ESTADO:0\n")

        self.robot.set_screen("dormido")

        while True:
            
            if self.robot.is_user_there():
                self.state = "DESPERTANDO"
                break
            else:
                # Caso en el que un usuario deja un residuo muy rápido
                if self.robot.is_waste_in_position():
                    self.state = "CLASIFICAR_1" # Se clasifica y segrega sin mayor interacción
                    break
                else:
                    continue

    def state_despertando(self):
        """Estado despertando: El robot espera a ver si hay un residuo en los próximos 3
        segundos. Si lo hay, pasa a 'clasificar_2', sino regresa a 'hibernacion'"""

        self.robot.ser.send(f"ESTADO:1\n")

        print("✅ Luces parpadean suavemente para incitar a la interacción")
        print("🔊 Reproducción de sonido de inicio")
        print("🤖 Expresión de robot despertando")

        self.robot.set_screen("despertando")
        
        inicio = time.time()

        while True:

            ahora = time.time()
            transcurrido = ahora - inicio  # Calcula los segundos transcurridos

            if self.robot.is_waste_in_position():
                self.state = "CLASIFICAR_2"
                break
            else:
                if transcurrido > 3:
                    self.state = "HIBERNACION"
                    break
                else:
                    continue
     
    def state_clasificar_1(self):
        """Estado clasificar_1: Estado en el que solamente se clasifica y segrega sin mayor 
        interacción con el usuario."""

        self.robot.ser.send(f"ESTADO:2\n")

        print("✅ Luces completamente encendidas")
        print("🔊 Reproducción de sonido alegre por recibir residuo")

        resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)

        if resultado:

            self.class_id, self.residuo, self.confianza = resultado
            print(f"Resultado: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}")
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")

            self.state = "HIBERNACION"
    
    def state_clasificar_2(self):
        """Estado clasificar_2: Estado en el que se clasifica, segrega y se interactúa con el
        usuario."""

        self.robot.ser.send(f"ESTADO:3\n")

        print("✅ Luces completamente encendidas")
        print("🔊 Reproducción de sonido alegre por recibir residuo")
        print("🤖 Expresión de robot feliz")

        self.robot.set_screen("feliz")

        resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)

        if resultado:

            self.class_id, self.residuo, self.confianza = resultado
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")

            print("✅ Encender luces con el color del contenedor al que va el residuo")
            print("🔊 Sonido random")

            print(f"Resultado: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}")
            self.robot.tts.deliver_message(f"Se detectó {self.residuo}.")
            
            self.robot.tts.deliver_message(f"¿Sabías que tu acción contribuye a la preservación
            de nuestro planeta y a una mayor generación de energía?")

            time.sleep(1)

            self.state = "AGRADECER"

    def state_agradecimiento(self):
        """Estado agradecimiento: Se agradece al usuario por reciclar, se reproducen sonidos alegres,
        se muestra una despedida en la pantalla y se activan luces en un cierto patrón."""

        self.robot.ser.send(f"ESTADO:4\n")

        self.robot.tts.deliver_message("Muchas gracias por reciclar! Espero verte pronto")
        # En producción: luz verde LED, sonido sutil, gesto mínimo del robot
        print("✅ Patrón de luces en el contenedor")
        print("🔊 Reproducción de sonido alegre")
        print("🤖 Expresión de despedida en la pantalla")

        time.sleep(3)

        self.state = "HIBERNACION"
