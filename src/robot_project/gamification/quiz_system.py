from typing import Dict, List, Optional, Tuple
import random

class QuizSystem:
    """Sistema de gamificación con banco de preguntas sobre reciclaje"""

    def __init__(self):
        self.questions_bank = self._load_questions()
        self.used_questions = set()

    def _load_questions(self) -> Dict[str, List[Dict]]:
        """Carga el banco de preguntas organizado por dificultad"""
        return {
            "basico": [
                {
                    "id": "q1",
                    "question": "¿Dónde va una caja de pizza con manchas de grasa?",
                    "options": [
                        {"key": "A", "text": "Orgánico", "icon": "🟢"},
                        {"key": "B", "text": "Papel", "icon": "🔵"},
                        {"key": "C", "text": "General", "icon": "⚫"}
                    ],
                    "correct": "C",
                    "explanation": "La grasa contamina el reciclaje de papel. Limpia = Papel, Con grasa = General"
                },
                {
                    "id": "q2",
                    "question": "¿Dónde va una botella de plástico vacía?",
                    "options": [
                        {"key": "A", "text": "Plástico", "icon": "🔵"},
                        {"key": "B", "text": "General", "icon": "⚫"},
                        {"key": "C", "text": "Papel", "icon": "📄"}
                    ],
                    "correct": "A",
                    "explanation": "Las botellas PET son 100% reciclables y van al contenedor de plástico"
                },
                {
                    "id": "q3",
                    "question": "¿Dónde va una lata de aluminio?",
                    "options": [
                        {"key": "A", "text": "General", "icon": "⚫"},
                        {"key": "B", "text": "Plástico", "icon": "🔵"},
                        {"key": "C", "text": "Metal/Plástico", "icon": "🔵"}
                    ],
                    "correct": "C",
                    "explanation": "El aluminio es altamente reciclable y ahorra 95% de energía vs producir uno nuevo"
                },
                {
                    "id": "q4",
                    "question": "¿Dónde va una caja de cartón limpia?",
                    "options": [
                        {"key": "A", "text": "Cartón", "icon": "📦"},
                        {"key": "B", "text": "General", "icon": "⚫"},
                        {"key": "C", "text": "Plástico", "icon": "🔵"}
                    ],
                    "correct": "A",
                    "explanation": "El cartón limpio es reciclable y se convierte en nuevo cartón o papel"
                },
                {
                    "id": "q5",
                    "question": "¿Dónde va un papel con restos de comida?",
                    "options": [
                        {"key": "A", "text": "Papel", "icon": "📄"},
                        {"key": "B", "text": "Orgánico", "icon": "🟢"},
                        {"key": "C", "text": "General", "icon": "⚫"}
                    ],
                    "correct": "C",
                    "explanation": "Los residuos de comida contaminan el papel reciclable, debe ir a general"
                }
            ],
            "intermedio": [
                {
                    "id": "q6",
                    "question": "¿Dónde va un envase Tetra Pak (caja de leche)?",
                    "options": [
                        {"key": "A", "text": "Papel", "icon": "📄"},
                        {"key": "B", "text": "Plástico", "icon": "🔵"},
                        {"key": "C", "text": "Requiere separación", "icon": "🔄"}
                    ],
                    "correct": "C",
                    "explanation": "Tetra Pak tiene capas de papel, plástico y aluminio. Idealmente se separan"
                },
                {
                    "id": "q7",
                    "question": "¿Dónde va una servilleta de papel usada?",
                    "options": [
                        {"key": "A", "text": "Papel", "icon": "📄"},
                        {"key": "B", "text": "Orgánico", "icon": "🟢"},
                        {"key": "C", "text": "General", "icon": "⚫"}
                    ],
                    "correct": "C",
                    "explanation": "Servilletas usadas tienen aceites y bacterias que contaminan el reciclaje"
                },
                {
                    "id": "q8",
                    "question": "¿Dónde va un vaso de café desechable con tapa?",
                    "options": [
                        {"key": "A", "text": "Todo a papel", "icon": "📄"},
                        {"key": "B", "text": "Todo a general", "icon": "⚫"},
                        {"key": "C", "text": "Separar: tapa→plástico, vaso→general", "icon": "🔄"}
                    ],
                    "correct": "C",
                    "explanation": "La tapa plástica es reciclable, pero el vaso tiene cera interior (no reciclable)"
                }
            ],
            "avanzado": [
                {
                    "id": "q9",
                    "question": "¿Dónde va una mascarilla quirúrgica usada?",
                    "options": [
                        {"key": "A", "text": "General", "icon": "⚫"},
                        {"key": "B", "text": "Orgánico", "icon": "🟢"},
                        {"key": "C", "text": "Peligroso", "icon": "☣️"}
                    ],
                    "correct": "A",
                    "explanation": "Las mascarillas NO son reciclables y van a residuos generales (no peligrosos)"
                },
                {
                    "id": "q10",
                    "question": "¿Dónde va una bombilla LED quemada?",
                    "options": [
                        {"key": "A", "text": "General", "icon": "⚫"},
                        {"key": "B", "text": "Electrónicos especiales", "icon": "⚡"},
                        {"key": "C", "text": "Plástico", "icon": "🔵"}
                    ],
                    "correct": "B",
                    "explanation": "Los LEDs contienen componentes electrónicos que requieren reciclaje especializado"
                }
            ]
        }

    def get_question_for_user(self, user_interactions: int,
                              used_questions: Optional[set] = None) -> Optional[Dict]:
        """
        Obtiene una pregunta apropiada según el nivel del usuario.

        Args:
            user_interactions: Número de interacciones previas del usuario
            used_questions: Set de IDs de preguntas ya usadas

        Returns:
            Dict con la pregunta, o None si no hay preguntas disponibles
        """
        if used_questions is None:
            used_questions = self.used_questions

        # Determinar nivel según interacciones
        if user_interactions < 5:
            level = "basico"
        elif user_interactions < 15:
            level = "intermedio"
        else:
            level = "avanzado"

        # Filtrar preguntas no usadas
        available_questions = [
            q for q in self.questions_bank[level]
            if q["id"] not in used_questions
        ]

        # Si no hay preguntas disponibles en ese nivel, intentar con básico
        if not available_questions and level != "basico":
            available_questions = [
                q for q in self.questions_bank["basico"]
                if q["id"] not in used_questions
            ]

        if not available_questions:
            # Reiniciar banco si se agotaron todas
            self.used_questions.clear()
            available_questions = self.questions_bank[level]

        if available_questions:
            question = random.choice(available_questions)
            self.used_questions.add(question["id"])
            return question

        return None

    def check_answer(self, question: Dict, user_answer: str) -> Tuple[bool, str]:
        """
        Verifica si la respuesta es correcta.

        Args:
            question: Dict de la pregunta
            user_answer: Letra de la respuesta del usuario

        Returns:
            Tuple (es_correcta, explicación)
        """
        is_correct = user_answer == question["correct"]
        return is_correct, question["explanation"]

    def calculate_points(self, is_correct: bool, base_points: int = 10) -> int:
        """
        Calcula puntos otorgados según la respuesta.

        Args:
            is_correct: Si la respuesta fue correcta
            base_points: Puntos base por respuesta correcta

        Returns:
            Puntos otorgados
        """
        if is_correct:
            return base_points
        else:
            return base_points // 2  # 50% por intento


class AchievementSystem:
    """Sistema de logros desbloqueables"""

    def __init__(self):
        self.achievements = self._load_achievements()

    def _load_achievements(self) -> List[Dict]:
        """Carga el catálogo de logros"""
        return [
            {
                "id": "aprendiz_verde",
                "nombre": "Aprendiz Verde",
                "descripcion": "10 reciclajes correctos",
                "icono": "🥉",
                "puntos": 50,
                "requisito": lambda stats: stats.get("correct_recycles", 0) >= 10
            },
            {
                "id": "guardian_eco",
                "nombre": "Guardián Eco",
                "descripcion": "50 reciclajes + 80% acierto en desafíos",
                "icono": "🥈",
                "puntos": 200,
                "requisito": lambda stats: (
                    stats.get("correct_recycles", 0) >= 50 and
                    stats.get("quiz_accuracy", 0) >= 0.8
                )
            },
            {
                "id": "perfeccionista",
                "nombre": "Perfeccionista",
                "descripcion": "10 reciclajes perfectos seguidos",
                "icono": "💎",
                "puntos": 300,
                "requisito": lambda stats: stats.get("perfect_streak", 0) >= 10
            },
            {
                "id": "reciclador_consciente",
                "nombre": "Reciclador Consciente",
                "descripcion": "Completó interacción nivel 3",
                "icono": "🌟",
                "puntos": 20,
                "requisito": lambda stats: stats.get("reached_level_3", False)
            }
        ]

    def check_new_achievements(self, user_stats: Dict,
                               unlocked_ids: set) -> List[Dict]:
        """
        Verifica si hay nuevos logros desbloqueados.

        Args:
            user_stats: Estadísticas del usuario
            unlocked_ids: Set de IDs de logros ya desbloqueados

        Returns:
            Lista de nuevos logros desbloqueados
        """
        new_achievements = []

        for achievement in self.achievements:
            if achievement["id"] not in unlocked_ids:
                if achievement["requisito"](user_stats):
                    new_achievements.append(achievement)
                    unlocked_ids.add(achievement["id"])

        return new_achievements
