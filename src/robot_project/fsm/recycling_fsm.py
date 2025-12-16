import time
import sys
import select

class RecyclingFSM:
    """
    Máquina de Estados Finitos para el sistema de reciclaje.
    
    WIZARD OF OZ MODE:
    - Presiona 'U' para simular detección de usuario
    - Presiona 'R' para simular detección de residuo
    - Los sensores VL53L0X NO se usan
    """

    def __init__(self, robot):
        self.robot = robot
        self.state = "HIBERNACION"
        self.class_id = None
        self.residuo = None
        self.confianza = None
        
        # Temporizadores
        self.state_timer_start = 0
        self.timer_duration_ms = 0
        
        # Flags de inicialización
        self._state_flags = {}
        
        # WIZARD OF OZ: Flags de control manual
        self.wizard_user_detected = False
        self.wizard_waste_detected = False

    def run(self):
        """
        Ejecuta la FSM con modo Wizard of Oz
        """
        try:
            print("\n" + "="*60)
            print("🎭 MODO WIZARD OF OZ ACTIVADO")
            print("="*60)
            print("Controles:")
            print("  [U] = Simular detección de usuario")
            print("  [R] = Simular detección de residuo")
            print("  [Ctrl+C] = Salir")
            print("="*60 + "\n")
            
            # Verificar si el display tiene pygame
            if hasattr(self.robot.display, 'running'):
                # Modo con pygame
                while self.robot.display.running:
                    if not self.robot.display.process_events():
                        break
                    
                    self.robot.display.update_animation()
                    
                    # WIZARD OF OZ: Leer teclas del usuario
                    self._check_wizard_input()
                    
                    # Ejecutar lógica del estado actual
                    getattr(self, f"state_{self.state.lower()}")()
            else:
                # Modo sin pygame
                while True:
                    # WIZARD OF OZ: Leer teclas del usuario
                    self._check_wizard_input()
                    
                    # Ejecutar lógica del estado actual
                    getattr(self, f"state_{self.state.lower()}")()
                    
                    time.sleep(0.1)  # Pequeña pausa
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Programa detenido")
            print("Enviando apagado al ESP32...")
            self.robot.ser.send("ESTADO:0\n")
            time.sleep(0.5)
        finally:
            if hasattr(self.robot.display, 'quit'):
                self.robot.display.quit()

    # ========== WIZARD OF OZ: LECTURA DE TECLAS ==========
    
    def _check_wizard_input(self):
        """
        Lee teclas del usuario para simular sensores.
        
        NO bloqueante - solo lee si hay entrada disponible.
        """
        # Verificar si hay entrada disponible (sin bloquear)
        if select.select([sys.stdin], [], [], 0.0)[0]:
            try:
                key = sys.stdin.read(1).upper()
                
                if key == 'U':
                    print("\n🎭 [WIZARD] Simulando: USUARIO DETECTADO")
                    self.wizard_user_detected = True
                    
                elif key == 'R':
                    print("\n🎭 [WIZARD] Simulando: RESIDUO DETECTADO")
                    self.wizard_waste_detected = True
                    
            except Exception as e:
                pass  # Ignorar errores de lectura

    # ========== UTILIDADES DE TEMPORIZADOR ==========
    
    def check_timer(self):
        """Verifica si el temporizador ha expirado"""
        if self.timer_duration_ms > 0:
            elapsed_time = time.time() * 1000 - self.state_timer_start
            if elapsed_time > self.timer_duration_ms:
                self.timer_duration_ms = 0
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
        Estado HIBERNACION: Espera tecla 'U' (usuario) o 'R' (residuo)
        """
        # Inicializar
        if not self.is_state_initialized('hibernacion'):
            print("\n💤 [HIBERNACION] Esperando input...")
            print("   Presiona [U] para simular usuario")
            print("   Presiona [R] para simular residuo rápido")
            self.robot.ser.send("ESTADO:0\n")
            
            if hasattr(self.robot.display, 'set_expression'):
                self.robot.display.set_expression("hibernando")
            
            self.mark_state_initialized('hibernacion')
        
        # Renderizar frame (si tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame()
        
        # WIZARD OF OZ: Verificar flags en lugar de sensores
        if self.wizard_user_detected:
            print("  ✅ Usuario detectado (WIZARD)")
            self.wizard_user_detected = False  # Reset flag
            self.reset_state_flag('hibernacion')
            self.state = "DESPERTANDO"
            return
        
        if self.wizard_waste_detected:
            print("  ✅ Residuo detectado (WIZARD - rápido)")
            self.wizard_waste_detected = False  # Reset flag
            self.reset_state_flag('hibernacion')
            self.state = "CLASIFICAR_1"
            return

    def state_despertando(self):
        """
        Estado DESPERTANDO: Espera tecla 'R' (residuo) o timeout
        """
        # Inicializar
        if not self.is_state_initialized('despertando'):
            print("\n👀 [DESPERTANDO] Robot despierta")
            print("   Presiona [R] para simular residuo")
            print("   O espera 5 segundos para timeout...")
            
            self.robot.ser.send("ESTADO:1\n")
            
            if hasattr(self.robot.display, 'set_expression'):
                self.robot.display.set_expression("despertando_inicio", loop=False)
            
            print("  🔊 [Audio] Sonido despertar")
            
            timer_duration = 5 if hasattr(self.robot.display, 'render_frame') else 3
            self.start_timer(timer_duration)
            
            self.mark_state_initialized('despertando')
        
        # Renderizar frame con texto (si tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Mmmmh? Hay alguien ahi?")
            
            animation_finished = self.robot.display.update_animation()
            if animation_finished and self.robot.display.current_state_name == "despertando_inicio":
                self.robot.display.set_expression("despertando_loop", loop=True)
        
        # WIZARD OF OZ: Verificar flag de residuo
        if self.wizard_waste_detected:
            print("  ✅ Residuo depositado (WIZARD)")
            self.robot.play_audio(self.robot.audio_paths["start_audio_path"])
            self.robot.tts.deliver_message("Hola! Qué tenemos aquí?")
            self.wizard_waste_detected = False  # Reset flag
            self.reset_state_flag('despertando')
            self.state = "CLASIFICAR_2"
            return
        
        # Verificar timeout
        if self.check_timer():
            print("  ⏱️ Timeout - Volviendo a HIBERNACION")
            self.robot.tts.deliver_message("Uhmmm? Bueno, volveré a dormir...")
            self.reset_state_flag('despertando')
            self.state = "HIBERNACION"
            return
     
    def state_clasificar_1(self):
        """
        Estado CLASIFICAR_1: Clasificación rápida sin interacción
        """
        # Inicializar
        if not self.is_state_initialized('clasificar1'):
            print("\n🔍 [CLASIFICAR_1] Clasificación rápida")
            self.robot.ser.send("ESTADO:2\n")
            print("  🔊 [Audio] Sonido alegre")
            
            self.mark_state_initialized('clasificar1')
            self._clasificacion_realizada = False
        
        # Renderizar frame (si tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Clasificando residuo...")

        # Clasificar UNA vez
        if not self._clasificacion_realizada:
            print("  📷 Clasificando con HailoVision...")
            
            try:
                resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)
                
                if resultado:
                    self.class_id, self.residuo, self.confianza = resultado
                    print(f"  ✅ {self.residuo} (id={self.class_id}, conf={self.confianza:.2f})")
                else:
                    print("  ⚠️ Clasificación falló, usando GENERAL")
                    self.class_id = 4
                    self.residuo = "Residuo General"
                    
            except Exception as e:
                print(f"  ⚠️ classify_waste() error: {e}")
                print("  📝 Usando simulación: Papel")
                self.class_id = 2
                self.residuo = "Papel"
            
            # Enviar al ESP32
            print(f"  📤 TX a ESP32: RESIDUO:{self.class_id}")
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
            
            self._clasificacion_realizada = True
            time.sleep(1)
            
            print("  ✅ Clasificación completada")
            self.reset_state_flag('clasificar1')
            self.state = "HIBERNACION"
    
    def state_clasificar_2(self):
        """
        Estado CLASIFICAR_2: Clasificación con interacción
        """
        # Inicializar
        if not self.is_state_initialized('clasificar2'):
            print("\n🔍 [CLASIFICAR_2] Clasificación con interacción")
            self.robot.ser.send("ESTADO:3\n")
            
            if hasattr(self.robot.display, 'set_expression'):
                self.robot.display.set_expression("feliz")
            
            print("  🔊 [Audio] Sonido alegre")
            
            self.mark_state_initialized('clasificar2')
            self._clasificacion_realizada = False
        
        # Renderizar frame (si tiene pygame)
        if hasattr(self.robot.display, 'render_frame'):
            self.robot.display.render_frame(text="Heeyy, cómo estás? Ven, acércate y ayúdame a reciclar!")
            self.robot.tts.deliver_message("Heeyy, cómo estás? Ven, acércate y ayúdame a reciclar!")

        # Clasificar UNA vez
        if not self._clasificacion_realizada:
            print("  📷 Clasificando con HailoVision...")
            
            try:
                resultado = self.robot.classify_waste(tiempo_limite=2, confianza_minima=0.3, mostrar=False)
                
                if resultado:
                    self.class_id, self.residuo, self.confianza = resultado
                    print(f"  ✅ {self.residuo} (id={self.class_id}, conf={self.confianza:.2f})")
                else:
                    print("  ⚠️ Clasificación falló, usando GENERAL")
                    self.class_id = 4
                    self.residuo = "Residuo General"
                    
            except Exception as e:
                print(f"  ⚠️ classify_waste() error: {e}")
                print("  📝 Usando simulación: Plástico")
                self.class_id = 3
                self.residuo = "Plástico"
            
            # Enviar al ESP32
            print(f"  📤 TX a ESP32: RESIDUO:{self.class_id}")
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
            
            # Mostrar resultado en pantalla (si tiene pygame)
            if hasattr(self.robot.display, 'render_frame'):
                self.robot.display.render_frame(text=f"¡Listo! Es {self.residuo}.")
                time.sleep(2)
            
            # Mensaje educativo con TTS
            print("  🗣️ [TTS] Mensaje educativo")
            try:
                self.robot.tts.deliver_message(f"¡Listo! Es {self.residuo}.")
            except Exception as e:
                print(f"  ⚠️ TTS error: {e}")
            
            self._clasificacion_realizada = True
            time.sleep(1)

            print("  ✅ Clasificación completada")
            self.reset_state_flag('clasificar2')
            self.state = "AGRADECIMIENTO"

    def state_agradecimiento(self):
        """
        Estado AGRADECIMIENTO: Despedida con QR
        """
        # Inicializar
        if not self.is_state_initialized('agradecimiento'):
            print("\n🎉 [AGRADECIMIENTO] Despedida")
            self.robot.ser.send("ESTADO:4\n")
            
            if hasattr(self.robot.display, 'set_expression'):
                self.robot.display.set_expression("feliz")
            
            print("  🔊 [Audio] Sonido alegre")
            self.robot.play_audio(self.robot.audio_paths["win_audio_path"])
            
            # TTS
            print("  🗣️ [TTS] Despedida")
            try:
                self.robot.tts.deliver_message("Muchas gracias por acompañarme! Te regalo 20 Peri-Puntos, escanea el QR y obtenlos.")
            except Exception as e:
                print(f"  ⚠️ TTS error: {e}")
            
            self.mark_state_initialized('agradecimiento')
            
            if hasattr(self.robot.display, 'render_frame'):
                self._showing_qr = False
                self._qr_timer_start = 0
                self._despedida_timer_start = 0
            else:
                self._simple_goodbye_timer = time.time()
        
        # Versión con pygame
        if hasattr(self.robot.display, 'render_frame'):
            if not self._showing_qr:
                self.robot.display.render_frame(
                    text="Muchas gracias por acompañarme! Te regalo 20 Peri-Puntos, escanea el QR y obtenlos.",
                    show_qr=True
                )
                if self._qr_timer_start == 0:
                    self._qr_timer_start = time.time()
            
            if self._qr_timer_start > 0 and (time.time() - self._qr_timer_start) > 3:
                if not self._showing_qr:
                    self._showing_qr = True
                    self.robot.display.set_expression("despedida")
                    try:
                        self.robot.tts.deliver_message("Espero verte pronto. Bai!")
                    except:
                        pass
                    self._despedida_timer_start = time.time()
            
            if self._showing_qr:
                self.robot.display.render_frame(text="Bai!")
                
                if (time.time() - self._despedida_timer_start) > 2:
                    print("  ✅ Despedida completada\n")
                    self.reset_state_flag('agradecimiento')
                    self.state = "HIBERNACION"
        
        # Versión simple
        else:
            if hasattr(self.robot.display, 'set_expression'):
                self.robot.display.set_expression("despedida")
            
            try:
                self.robot.tts.deliver_message("Espero verte pronto")
            except:
                pass

            if (time.time() - self._simple_goodbye_timer) > 3:
                print("  ✅ Despedida completada\n")
                self.reset_state_flag('agradecimiento')
                self.state = "HIBERNACION"
