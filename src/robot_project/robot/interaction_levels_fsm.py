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
    Implementa los niveles 1-3 del sistema de interacción educativa.
    """

    def __init__(self, robot):
        self.robot = robot
        self.config = load_config()
        self.levels_config = self.config.get("interaction_levels", {})

        # Componentes del sistema de niveles
        self.proximity_sensor = MockProximitySensor()
        self.display = MockDisplay()
        self.quiz_system = QuizSystem()
        self.achievement_system = AchievementSystem()
        self.impact_calculator = ImpactCalculator(
            location=self.levels_config.get("level_3", {}).get("location", "Lima")
        )

        # Estado del sistema
        self.state = "INICIO"
        self.class_id = None
        self.residuo = None
        self.confianza = None
        self.student_code = None
        self.current_student_stats = None
        self.ppi = 0.0  # Puntaje de Propensión a la Interacción
        self.quiz_streak = 0  # Racha actual de respuestas correctas

        # Umbrales de configuración
        self.ppi_threshold = self.levels_config.get("ppi_threshold", 0.6)

    def run(self):
        """Ejecuta la FSM de niveles de interacción"""
        try:
            while True:
                getattr(self, f"state_{self.state.lower()}")()
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del programa de niveles")

    def calculate_ppi(self, student_stats: Optional[Dict] = None, approach_time: float = 1.0) -> float:
        """
        Calcula el Puntaje de Propensión a la Interacción (PPI).
        PPI simplificado basado en: historial del usuario + tiempo de aproximación.

        Args:
            student_stats: Estadísticas del estudiante (si está identificado)
            approach_time: Tiempo de aproximación antes de depositar (segundos)

        Returns:
            float: PPI entre 0.0 y 1.0
        """
        base = 0.5  # PPI base para usuarios nuevos

        # Factor histórico (si hay estadísticas de usuario)
        if student_stats:
            interactions = student_stats.get("total_interactions", 0)
            if interactions > 10:
                base += 0.2
            elif interactions > 3:
                base += 0.1

            # Bonus por tasa de acierto alta
            quiz_accuracy = student_stats.get("quiz_accuracy", 0)
            if quiz_accuracy > 0.8:
                base += 0.05

        # Factor de tiempo de aproximación
        if approach_time > 3:
            base += 0.15
        elif approach_time > 1:
            base += 0.05

        return min(base, 1.0)

    def state_inicio(self):
        """Estado inicial: espera comando y mide PPI"""
        self.robot.play_audio(self.robot.audio_paths["start_audio_path"])
        self.robot.tts.deliver_message("Hola, soy Peri. Reciclemos juntos!")

        while True:
            self.robot.start_listening_threads()
            command = self.robot.get_response()

            if command.lower() in ["reciclar", "recicla esto", "por favor recicla esto",
                                   "ayúdame con esto", "ayúdame a reciclar esto"]:
                # Medir tiempo de aproximación (simulado)
                approach_time = self.proximity_sensor.measure_approach_time()

                # Intentar obtener código de estudiante para calcular PPI personalizado
                self.robot.tts.deliver_message("Si tienes un código de estudiante, dímelo ahora. Si no, di 'no tengo'")
                self.robot.start_listening_threads()
                response = self.robot.get_response()

                if response.lower() not in ["no tengo", "no", "continuar", "siguiente"]:
                    code = self.robot.text_to_number(response)
                    if code != 0:
                        self.student_code = code
                        self.current_student_stats = self.robot.student_db.get_student_stats(code)

                # Calcular PPI
                self.ppi = self.calculate_ppi(self.current_student_stats, approach_time)
                print(f"\n📊 PPI calculado: {self.ppi:.2f} (umbral: {self.ppi_threshold})")

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
        """Clasifica el residuo y decide ruta según PPI"""
        resultado = self.robot.classify_waste()

        if resultado:
            self.class_id, self.residuo, self.confianza = resultado
            print(f"Resultado: {self.residuo} (id {self.class_id}) con confianza {self.confianza:.2f}")

            self.robot.tts.deliver_message(f"Se detectó {self.residuo}.")
            self.robot.ser.send(f"RESIDUO:{self.class_id}\n")
            time.sleep(0.5)

            is_full = False  # Simulado: self.robot.is_trash_can_full(self.class_id)

            if not is_full:
                # Decidir ruta según PPI
                if self.ppi >= self.ppi_threshold:
                    print(f"✅ PPI >= {self.ppi_threshold} → Ruta educativa (Niveles)")
                    self.state = "NIVEL_1"
                else:
                    print(f"ℹ️  PPI < {self.ppi_threshold} → Retroalimentación mínima")
                    self.retroalimentacion_minima()
                    self.state = "INICIO"
            else:
                self.robot.tts.deliver_message(
                    f"Lo lamento, mi contenedor para {self.residuo} está lleno. "
                    "Por favor colócalo en otro tacho. ¡Gracias por ayudar a reciclar!"
                )
                self.state = "INICIO"
        else:
            print("No se detectó ningún residuo válido.")
            self.state = "INICIO"

    def retroalimentacion_minima(self):
        """Retroalimentación mínima para usuarios pragmáticos (PPI < umbral)"""
        print("\n💚 RETROALIMENTACIÓN AMBIENTAL (< 1 segundo)")
        self.robot.tts.deliver_message("Listo!")
        # En producción: luz verde LED, sonido sutil, gesto mínimo del robot
        print("✅ Luz verde en contenedor")
        print("🔊 Sonido sutil de confirmación (200ms)")
        print("🤖 Gesto mínimo del robot (asentimiento)")
        time.sleep(0.5)

    def state_nivel_1(self):
        """NIVEL 1: Retroalimentación directa y relevante"""
        print("\n🎯 NIVEL 1: Retroalimentación Directa")

        # Determinar si fue correcta (en este caso, siempre es correcta porque usamos CV)
        is_correct = True  # La CV ya clasificó correctamente

        # Obtener información de impacto
        impact = self.impact_calculator.calculate_single_item_impact(self.residuo)

        # Mostrar en pantalla y voz
        if is_correct:
            self.robot.tts.deliver_message(
                f"¡Genial! Ese {self.residuo} va justo en el contenedor correcto. "
                f"{impact['descripcion']}"
            )
            self.display.show_classification_result(
                correct=True,
                item=self.residuo,
                container="contenedor correcto",
                extra_info=impact['descripcion']
            )

        # Actualizar estadísticas si hay estudiante identificado
        if self.student_code:
            self.robot.student_db.update_recycling_stats(
                self.student_code, self.residuo, is_correct
            )

        # Sensor de permanencia → ¿Continuar a Nivel 2?
        permanence_threshold = self.levels_config.get("level_2", {}).get("permanence_threshold_seconds", 2)

        if self.proximity_sensor.detect_user_presence(permanence_threshold):
            self.state = "NIVEL_2"
        else:
            self.robot.tts.deliver_message("Gracias por reciclar! Hasta pronto!")
            self.state = "INICIO"

    def state_nivel_2(self):
        """NIVEL 2: Desafío cognitivo (Gamificación)"""
        print("\n🎮 NIVEL 2: Gamificación y Desafío")

        self.robot.tts.deliver_message("Pareces interesado en el reciclaje. ¡Una pregunta rápida!")

        # Obtener pregunta apropiada según nivel del usuario
        user_interactions = 0
        if self.current_student_stats:
            user_interactions = self.current_student_stats.get("total_interactions", 0)

        question = self.quiz_system.get_question_for_user(user_interactions)

        if not question:
            self.robot.tts.deliver_message("Ups, me quedé sin preguntas. ¡Sigamos adelante!")
            self.state = "NIVEL_3"
            return

        # Mostrar pregunta en pantalla y obtener respuesta
        quiz_timer = self.levels_config.get("level_2", {}).get("quiz_timer_seconds", 10)

        self.robot.tts.deliver_message(question["question"])
        user_answer = self.display.show_quiz_question(
            question=question["question"],
            options=question["options"],
            timer_seconds=quiz_timer
        )

        # Verificar respuesta
        is_correct, explanation = self.quiz_system.check_answer(question, user_answer)
        points_correct = self.levels_config.get("level_2", {}).get("points_correct", 10)
        points_attempt = self.levels_config.get("level_2", {}).get("points_attempt", 5)
        points_earned = self.quiz_system.calculate_points(is_correct, points_correct)

        # Actualizar racha
        if is_correct:
            self.quiz_streak += 1
        else:
            self.quiz_streak = 0

        # Mostrar resultado
        if is_correct:
            self.robot.tts.deliver_message(f"¡Correcto! {explanation}")
        else:
            self.robot.tts.deliver_message(f"Buen intento! {explanation}")

        self.display.show_quiz_result(
            correct=is_correct,
            selected=user_answer or "ninguna",
            correct_answer=question["correct"],
            points=points_earned,
            explanation=explanation,
            streak=self.quiz_streak
        )

        # Actualizar estadísticas de quiz
        if self.student_code:
            self.robot.student_db.update_quiz_stats(self.student_code, is_correct, points_earned)

        # Sensor de atención y permanencia → ¿Continuar a Nivel 3?
        permanence_threshold = self.levels_config.get("level_3", {}).get("permanence_threshold_seconds", 3)

        if self.proximity_sensor.detect_attention() and \
           self.proximity_sensor.detect_user_presence(permanence_threshold):
            self.state = "NIVEL_3"
        else:
            self.robot.tts.deliver_message("Genial! Gracias por participar. Hasta pronto!")
            self.state = "INICIO"

    def state_nivel_3(self):
        """NIVEL 3: Conexión personalizada y estadísticas de impacto"""
        print("\n🌍 NIVEL 3: Impacto Personalizado")

        # Generar mensaje de impacto local
        local_impact_msg = self.impact_calculator.get_local_impact_message(self.residuo, 1)
        self.robot.tts.deliver_message(
            f"Gracias a tu acción de reciclar ese {self.residuo}, {local_impact_msg}"
        )

        # Si hay usuario identificado, mostrar estadísticas acumuladas
        if self.student_code and self.current_student_stats:
            recycling_history = self.current_student_stats.get("recycling_history", {})
            accumulated_impact = self.impact_calculator.calculate_accumulated_impact(recycling_history)
            formatted_impact = self.impact_calculator.format_impact_for_display(accumulated_impact)

            # Calcular ranking (simulado)
            percentile = 85  # Top 15% (simulado)
            district = self.levels_config.get("level_3", {}).get("district", "")
            ranking_msg = self.impact_calculator.get_ranking_message(percentile, district)

            # Mostrar en pantalla
            self.display.show_impact_stats(
                item=self.residuo,
                local_impact=local_impact_msg,
                total_recycled=accumulated_impact["total_items"],
                total_impact=formatted_impact,
                ranking=ranking_msg
            )

            self.robot.tts.deliver_message(
                f"En total has reciclado {accumulated_impact['total_items']} items. "
                f"Has ahorrado {accumulated_impact['energia_horas']} horas de energía. {ranking_msg}"
            )

            # Marcar que alcanzó nivel 3
            self.robot.student_db.mark_level_reached(self.student_code, 3)

            # Verificar logros desbloqueados
            updated_stats = self.robot.student_db.get_student_stats(self.student_code)
            unlocked_ids = updated_stats.get("unlocked_achievements", set())
            new_achievements = self.achievement_system.check_new_achievements(updated_stats, unlocked_ids)

            for achievement in new_achievements:
                self.robot.student_db.unlock_achievement(self.student_code, achievement["id"])
                self.display.show_achievement_unlocked(
                    achievement_name=achievement["nombre"],
                    achievement_icon=achievement["icono"],
                    description=achievement["descripcion"],
                    points=achievement["puntos"]
                )
                self.robot.tts.deliver_message(
                    f"¡Felicitaciones! Desbloqueaste el logro {achievement['nombre']}"
                )
                time.sleep(2)

        # Finalizar interacción
        self.robot.tts.deliver_message("¡Eres un campeón del reciclaje! Hasta pronto!")
        self.state = "INICIO"
        time.sleep(3)

    def state_conversacion(self):
        """Estado de conversación (modo legacy compatible)"""
        self.robot.start_listening_threads()
        command = self.robot.get_response()

        if command:
            print(f"🗣️ texto reconocido: {command}")
            if command.lower() in ["adios", "adiós"]:
                self.robot.tts.deliver_message("Me gustó hablar contigo. ¡Hasta pronto!")
                self.state = "INICIO"
                time.sleep(5)
            else:
                respuesta = self.robot.llm.ask_llm(command)
                self.robot.tts.deliver_message(respuesta)
        else:
            self.robot.tts.deliver_message("No entendí eso. ¿Puedes repetirlo?")
