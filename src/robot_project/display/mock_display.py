import time
from typing import Optional, List, Dict

class MockDisplay:
    """Mock de pantalla táctil para mostrar información visual"""

    def __init__(self):
        self.current_screen = None

    def show_feedback_box(self, title: str, lines: List[str], icon: str = ""):
        """
        Muestra un cuadro de retroalimentación visual simulado.

        Args:
            title: Título del cuadro
            lines: Lista de líneas de texto
            icon: Emoji o icono opcional
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ {icon} {title:<{width-4}} │")
        print("│" + " " * width + "│")

        for line in lines:
            # Dividir líneas largas
            if len(line) > width - 4:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) < width - 4:
                        current_line += word + " "
                    else:
                        print(f"│ {current_line:<{width-2}} │")
                        current_line = word + " "
                if current_line:
                    print(f"│ {current_line:<{width-2}} │")
            else:
                print(f"│ {line:<{width-2}} │")

        print("└" + "─" * width + "┘")

    def show_classification_result(self, correct: bool, item: str, container: str,
                                   extra_info: str = ""):
        """
        Muestra el resultado de clasificación (Nivel 1).

        Args:
            correct: Si fue correcta la clasificación
            item: Nombre del residuo
            container: Contenedor correcto
            extra_info: Información adicional educativa
        """
        if correct:
            self.show_feedback_box(
                "✓ ¡Correcto!",
                [
                    f"🗑️  {item} → {container}",
                    extra_info if extra_info else ""
                ],
                "✅"
            )
        else:
            self.show_feedback_box(
                "ℹ️ Te ayudo con eso",
                [
                    f"🗑️  {item} → {container}",
                    extra_info if extra_info else ""
                ],
                "🤖"
            )

    def show_quiz_question(self, question: str, options: List[Dict[str, str]],
                          timer_seconds: int = 10) -> Optional[str]:
        """
        Muestra una pregunta de quiz (Nivel 2).

        Args:
            question: Texto de la pregunta
            options: Lista de opciones [{'key': 'A', 'text': 'Orgánico', 'icon': '🟢'}]
            timer_seconds: Segundos para responder

        Returns:
            Letra de la opción seleccionada (A, B, C)
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ 🎮 DESAFÍO RÁPIDO{' ' * (width - 18)}│")
        print("│" + " " * width + "│")
        print(f"│ {question:<{width-2}} │")
        print("│" + " " * width + "│")

        for opt in options:
            opt_text = f"  [{opt['key']}] {opt['icon']} {opt['text']}"
            print(f"│ {opt_text:<{width-2}} │")

        print("│" + " " * width + "│")
        print(f"│ ⏱️  {timer_seconds} segundos{' ' * (width - 17)}│")
        print("└" + "─" * width + "┘")

        # Simular selección
        print(f"\n[PANTALLA TÁCTIL] Selecciona una opción ({', '.join([o['key'] for o in options])}): ", end="")
        response = input().strip().upper()

        if response in [o['key'] for o in options]:
            return response
        else:
            print("⚠️ Opción inválida, se considera sin respuesta")
            return None

    def show_quiz_result(self, correct: bool, selected: str, correct_answer: str,
                        points: int, explanation: str, streak: int = 0):
        """
        Muestra el resultado de un quiz (Nivel 2).

        Args:
            correct: Si la respuesta fue correcta
            selected: Opción seleccionada
            correct_answer: Opción correcta
            points: Puntos ganados
            explanation: Explicación educativa
            streak: Racha de respuestas correctas
        """
        if correct:
            streak_stars = "⭐" * min(streak, 5)
            self.show_feedback_box(
                f"✓ ¡CORRECTO! +{points} puntos",
                [
                    explanation,
                    f"Racha: {streak_stars} ({streak} seguidas)" if streak > 0 else ""
                ],
                "🎉"
            )
        else:
            self.show_feedback_box(
                f"ℹ️ Casi... +{points // 2} puntos",
                [
                    f"Respuesta correcta: {correct_answer}",
                    f"💡 {explanation}"
                ],
                "📚"
            )

    def show_impact_stats(self, item: str, local_impact: str,
                         total_recycled: int, total_impact: Dict[str, str],
                         ranking: str = ""):
        """
        Muestra estadísticas de impacto personalizadas (Nivel 3).

        Args:
            item: Residuo reciclado
            local_impact: Impacto local específico
            total_recycled: Total de items reciclados por el usuario
            total_impact: Dict con impactos acumulados
            ranking: Posición en ranking (opcional)
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ 🌍 TU IMPACTO HOY{' ' * (width - 16)}│")
        print("│" + " " * width + "│")
        print(f"│ {local_impact:<{width-2}} │")
        print("│" + " " * width + "│")
        print(f"│ 📊 TU IMPACTO TOTAL:{' ' * (width - 22)}│")
        print(f"│ • {total_recycled} items reciclados{' ' * (width - 25 - len(str(total_recycled)))}│")

        for key, value in total_impact.items():
            line = f"• {value}"
            print(f"│ {line:<{width-2}} │")

        if ranking:
            print("│" + " " * width + "│")
            print(f"│ {ranking:<{width-2}} │")

        print("└" + "─" * width + "┘")

    def show_achievement_unlocked(self, achievement_name: str, achievement_icon: str,
                                  description: str, points: int):
        """
        Muestra un logro desbloqueado.

        Args:
            achievement_name: Nombre del logro
            achievement_icon: Icono del logro
            description: Descripción
            points: Puntos otorgados
        """
        self.show_feedback_box(
            "🏆 ¡LOGRO DESBLOQUEADO!",
            [
                f"{achievement_icon} {achievement_name}",
                description,
                f"🎁 +{points} Eco-Puntos"
            ],
            "✨"
        )

    def clear(self):
        """Limpia la pantalla (simula borrado de display)."""
        print("\n" + "🖥️  [DISPLAY] Pantalla limpiada\n")
