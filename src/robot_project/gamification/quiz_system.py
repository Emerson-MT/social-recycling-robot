from typing import Dict, List, Optional, Tuple
import random
from pathlib import Path
import json

class QuizSystem:
    """Sistema de gamificación con preguntas de VERDADERO/FALSO sobre reciclaje"""

    def __init__(self, language):
        self.language = language
        self.used_questions = set()
        self.questions_bank = self._load_questions()

    def _load_questions(self) -> Dict[str, List[Dict]]:
        """
        Carga el banco de preguntas desde el JSON basándose en el parámetro 'language'.
        Ruta: src/robot_project/configs/questions.json
        """
        # Definición de la ruta usando Path
        QUESTIONS_PATH = Path(__file__).resolve().parent.parent / "configs" / "questions.json"
        
        try:
            if not QUESTIONS_PATH.exists():
                print(f"❌ Error: El archivo no existe en {QUESTIONS_PATH}")
                return {"basico": [], "intermedio": [], "avanzado": []}

            with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Retornar las preguntas del idioma solicitado o un dict vacío si no existe
            return data.get(self.language, {"basico": [], "intermedio": [], "avanzado": []})

        except json.JSONDecodeError:
            print(f"❌ Error: El archivo JSON tiene un formato inválido.")
            return {"basico": [], "intermedio": [], "avanzado": []}
        except Exception as e:
            print(f"❌ Error inesperado al cargar preguntas: {e}")
            return {"basico": [], "intermedio": [], "avanzado": []}

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
        elif user_interactions < 12:
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

    def check_answer(self, question: Dict, user_answer: bool) -> Tuple[bool, str]:
        """
        Verifica si la respuesta es correcta.

        Args:
            question: Dict de la pregunta
            user_answer: True o False

        Returns:
            Tuple (es_correcta, explicación)
        """
        is_correct = user_answer == question["correct"]
        return is_correct, question["explanation"]

    def calculate_points(self, is_correct: bool, base_points: int = 15) -> int:
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
            return base_points // 15  # 1% por intento


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
            },
            {
                "id": "maestro_quiz",
                "nombre": "Maestro del Quiz",
                "descripcion": "Respondió 20 preguntas correctamente",
                "icono": "🎓",
                "puntos": 150,
                "requisito": lambda stats: stats.get("correct_quiz_answers", 0) >= 20
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
