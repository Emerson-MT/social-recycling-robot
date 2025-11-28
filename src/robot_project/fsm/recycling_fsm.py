import time

class RecyclingFSM:
    """
    Máquina de Estados Finitos para el sistema de reciclaje.
    
    MERGED VERSION: Combina la lógica robusta de recycling_fsm.py con 
    las mejoras de integración pygame y temporizadores de fsm_ale.py
    """

    def __init__(self, robot):
        self.robot = robot
        self.state = "HIBERNACION"  # Estado inicial (de recycling_fsm.py)
        self.class_id = None
        self.residuo = None
        self.confianza = None
        
        # ========== MEJORAS DE fsm_ale.py ==========
        # Temporizadores para transiciones automáticas
        self.state_timer_start = 0
        self.timer_duration_ms = 0
        
        # Flags de inicialización por estado (evita re-ejecución)
        self._state_flags = {}

    def run(self):
        """
        Ejecuta la FSM de niveles de interacción con actualización continua de display.
        
        MERGED: Combina el loop básico de recycling_fsm.py con la integración 
        pygame de fsm_ale.py
        """
        try:
            # Verificar si el display tiene pygame (fsm_ale.py)
            if hasattr(self.robot.display, 'running'):
                # Modo con pygame
                while self.robot.display.running:
                    # Procesar eventos de pygame (cerrar ventana, ESC, etc)
                    if not self.robot.display.process_events():
                        break
                    
                    # Actualizar animación
                    self.robot.display.update_animation()
                    
                    # Ejecutar lógica del estado actual
                    getattr(self, f"state_{self.state.lower()}")()
            else:
                # Modo sin pygame (recycling_fsm.py original)
                while True:
                    getattr(self, f"state_{self.state.lower()}")()
                    
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del programa de niveles")
        finally:
            # Cerrar display si existe (fsm_ale.py)
            if hasattr(self.robot.display, 'quit'):
                self.robot.display.quit()

    # ========== UTILIDADES DE TEMPORIZADOR (de fsm_ale.py) ==========
    
    def check_timer(self):
        """Verifica si el temporizador ha expirado"""
        if self.timer_duration_ms > 0:
            elapsed_time = time.time() * 1000 - self.state_timer_start
            if elapsed_time > self.timer_duration_ms:
                self.timer_duration_ms = 0  # Desactiva el temporizador
                return True
        return False
    
    def start_timer(self, duration_seconds):
        """Inicia un temporizador para transiciones automáticas"""
        self.state_timer_start = time.time() * 1000
        self.timer_duration_ms = duration_seconds * 1000
    
    def reset_state_flag(self, state_name):
        """Resetea el flag de inicialización de un estado"""
        flag_name = f'_{state_name}_initialized'
        if hasattr(self, flag_name):
            delattr(self, flag_name)
    
    def is_state_initialized(self, state_name):
        """Verifica si un estado ya fue inicializado"""
        flag_name = f'_{state_name}_initialized'
        return hasattr(self, flag_name)
    
    def mark_state_initialized(self, state_name):
        """Marca un estado como inicializado"""
        flag_name = f'_{state_name}_initialized'
        setattr(self, flag_name, True)

    # ========== ESTADOS DE LA FSM ==========

    def state_hibernacion(self):
        """
        Estado hibernacion: Espera a que haya un usuario para entrar al estado 'despertando'
        o que haya un residuo en posición para continuar al estado 'clasificar_1'.
        
        MERGED: Lógica de recycling_fsm.py + mejoras visuales de fsm_ale.py
        """
        # Inicializar solo una vez al entrar al estado
        if not self.is_state_initialized('hibernacion'):
            self.robot.ser.send(f"ESTADO:0\n")
            self.robot.display.set_expression("hibernando")
            print("💤 Robot en hibernación...")
            self.mark_state_initialized('hibernacion')
        
        # Renderizar frame (si display tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame()
        
        # Verificar presencia de usuario
        user_there = self.robot.is_user_there()

        if user_there:
            self.reset_state_flag('hibernacion')
            self.state = "DESPERTANDO"
            return
        
        # Caso en el que un usuario deja un residuo muy rápido
        waste_in_position = self.robot.is_waste_in_position()

        if waste_in_position:
            self.reset_state_flag('hibernacion')
            self.state = "CLASIFICAR_1"
            return

    def state_despertando(self):
        """
        Estado despertando: El robot espera a ver si hay un residuo en los próximos 3-5
        segundos. Si lo hay, pasa a 'clasificar_2', sino regresa a 'hibernacion'.
        
        MERGED: Lógica de recycling_fsm.py + temporizadores y animaciones de fsm_ale.py
        """
        # Inicializar solo una vez
        if not self.is_state_initialized('despertando'):
            self.robot.ser.send(f"ESTADO:1\n")
            print("✨ Luces parpadean suavemente para incitar a la interacción")
            
            # Reproducir sonido de inicio
            # self.robot.play_audio('mp3_path')
            print("🔊 Reproducción de sonido de inicio")
            
            # Animación de despertar
            if hasattr(self.robot.display, 'set_expression'):
                # Versión con pygame: usar animación de inicio no-loop
                self.robot.display.set_expression("despertando_inicio", loop=False)
            else:
                # Versión simple: solo expresión genérica
                self.robot.display.set_expression("despertando")
            
            print("🤖 Expresión de robot despertando")
            
            # Iniciar temporizador (5 segundos si tiene pygame, 3 si no)
            timer_duration = 5 if hasattr(self.robot.display, 'render_frame') else 3
            self.start_timer(timer_duration)
            
            self.mark_state_initialized('despertando')
        
        # Renderizar frame con texto (si display tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Mmmmh? Hay alguien ahi?")
            
            # Verificar si la animación inicial terminó para cambiar al loop
            animation_finished = self.robot.display.update_animation()
            if animation_finished and self.robot.display.current_state_name == "despertando_inicio":
                self.robot.display.set_expression("despertando_loop", loop=True)
        
        # Verificar residuo en posición
        waste_in_position = self.robot.is_waste_in_position()

        if waste_in_position:
            self.reset_state_flag('despertando')
            self.state = "CLASIFICAR_2"
            return
        
        # Verificar si expiró el temporizador
        if self.check_timer():
            print("⏰ Usuario no interactuó a tiempo, volviendo a dormir...")
            self.reset_state_flag('despertando')
            self.state = "HIBERNACION"
            return
     
    def state_clasificar_1(self):
        """
        Estado clasificar_1: Estado en el que solamente se clasifica y segrega sin mayor 
        interacción con el usuario.
        
        MERGED: Lógica de recycling_fsm.py + mejoras visuales de fsm_ale.py
        """
        # Inicializar solo una vez
        if not self.is_state_initialized('clasificar1'):
            self.robot.ser.send(f"ESTADO:2\n")
            print("✅ Luces completamente encendidas")

            # Reproducir sonido alegre
            # self.robot.play_audio('mp3_path')
            print("🔊 Reproducción de sonido alegre por recibir residuo")

            self.mark_state_initialized('clasificar1')
            self._clasificacion_realizada = False
        
        # Renderizar frame (si display tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Clasificando residuo...")

        # Realizar clasificación solo una vez
        if not self._clasificacion_realizada:
            resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)

            if resultado:
                self.class_id, self.residuo, self.confianza = resultado
                print(f"Resultado: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}")
                
                self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
                
                self._clasificacion_realizada = True
                time.sleep(1)  # Breve pausa antes de volver a hibernación
                
                self.reset_state_flag('clasificar1')
                self.state = "HIBERNACION"
    
    def state_clasificar_2(self):
        """
        Estado clasificar_2: Estado en el que se clasifica, segrega y se interactúa con el
        usuario.
        
        MERGED: Lógica de recycling_fsm.py + mejoras visuales y TTS de fsm_ale.py
        """
        # Inicializar solo una vez
        if not self.is_state_initialized('clasificar2'):
            self.robot.ser.send(f"ESTADO:3\n")
            print("✅ Luces completamente encendidas")
            
            # Reproducir sonido alegre
            # self.robot.play_audio('mp3_path')
            print("🔊 Reproducción de sonido alegre por recibir residuo")

            self.robot.display.set_expression("feliz")
            print("🤖 Expresión de robot feliz")
            
            self.mark_state_initialized('clasificar2')
            self._clasificacion_realizada = False
        
        # Renderizar frame con texto de invitación (si display tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Heeyy, como estas? Ven, acercate y ayudame a reciclar!")

        # Realizar clasificación solo una vez
        if not self._clasificacion_realizada:
            resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)

            if resultado:
                self.class_id, self.residuo, self.confianza = resultado
                
                self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
                print("✅ Encender luces con el color del contenedor al que va el residuo")

                # Reproducir sonido random
                # self.robot.play_audio('mp3_path')
                print("🔊 Sonido random")

                print(f"Resultado: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}")
                
                # Mostrar resultado en pantalla (si display tiene pygame)
                if hasattr(self.robot.display, 'render_frame'):
                    self.robot.display.render_frame(text=f"¡Listo! Es {self.residuo}.")
                    time.sleep(2)
                
                # Mensaje educativo con TTS
                self.robot.tts.deliver_message(f"Se detectó {self.residuo}.")
                self.robot.tts.deliver_message(f"¿Sabías que tu acción contribuye a la preservación de nuestro planeta y a una mayor generación de energía?")

                self._clasificacion_realizada = True
                time.sleep(1)

                self.reset_state_flag('clasificar2')
                self.state = "AGRADECIMIENTO"

    def state_agradecimiento(self):
        """
        Estado agradecimiento: Se agradece al usuario por reciclar, se reproducen sonidos alegres,
        se muestra una despedida en la pantalla y se activan luces en un cierto patrón.
        
        MERGED: Lógica de recycling_fsm.py + sistema de QR y temporizadores de fsm_ale.py
        """
        # Inicializar solo una vez
        if not self.is_state_initialized('agradecimiento'):
            self.robot.ser.send(f"ESTADO:4\n")
            print("✅ Luces con patrón alegre de despedida")

            # Reproducir sonido alegre
            # self.robot.play_audio('mp3_path')
            print("🔊 Reproducción de sonido alegre")

            self.robot.display.set_expression("feliz")
            print("🤖 Expresión feliz en la pantalla")

            # Mensaje de agradecimiento
            self.robot.tts.deliver_message("Muchas gracias por reciclar!")
            
            self.mark_state_initialized('agradecimiento')
            
            # Variables para control de flujo
            if hasattr(self.robot.display, 'render_frame'):
                # Versión con pygame: mostrar QR y temporizadores
                self._showing_qr = False
                self._qr_timer_start = 0
                self._despedida_timer_start = 0
            else:
                # Versión simple: solo esperar y volver
                self._simple_goodbye_timer = time.time()
        
        # ========== VERSIÓN CON PYGAME (de fsm_ale.py) ==========
        if hasattr(self.robot.display, 'render_frame'):
            # Mostrar código QR con recompensa por 3 segundos
            if not self._showing_qr:
                self.robot.display.render_frame(
                    text="Muchas gracias por acompaÃ±arme! Te regalo 20 Peri-Puntos, escanea el QR y obtenlos.",
                    show_qr=True
                )
                if self._qr_timer_start == 0:
                    self._qr_timer_start = time.time()
            
            # Después de 3 segundos con QR, mostrar despedida
            if self._qr_timer_start > 0 and (time.time() - self._qr_timer_start) > 3:
                if not self._showing_qr:
                    self._showing_qr = True
                    self.robot.display.set_expression("despedida")
                    self.robot.tts.deliver_message("Espero verte pronto. Byeeee!")
                    self._despedida_timer_start = time.time()
            
            # Renderizar despedida
            if self._showing_qr:
                self.robot.display.render_frame(text="Byeeee")
                
                # Después de 2 segundos de despedida, volver a hibernación
                if (time.time() - self._despedida_timer_start) > 2:
                    self.reset_state_flag('agradecimiento')
                    self.state = "HIBERNACION"
        
        # ========== VERSIÓN SIMPLE (de recycling_fsm.py) ==========
        else:
            self.robot.display.set_expression("despedida")
            print("🤖 Expresión de despedida en la pantalla")

            self.robot.tts.deliver_message("Espero verte pronto")

            # Esperar 3 segundos y volver a hibernación
            if (time.time() - self._simple_goodbye_timer) > 3:
                self.reset_state_flag('agradecimiento')
                self.state = "HIBERNACION"
