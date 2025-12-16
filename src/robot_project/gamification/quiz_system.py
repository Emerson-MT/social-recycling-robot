from typing import Dict, List, Optional, Tuple
import random

class QuizSystem:
    """Sistema de gamificación con preguntas de VERDADERO/FALSO sobre reciclaje"""

    def __init__(self):
        self.questions_bank = self._load_questions()
        self.used_questions = set()

    def _load_questions(self) -> Dict[str, List[Dict]]:
        """Carga el banco de preguntas de verdadero/falso organizadas por dificultad"""
        return {
            "basico": [
                {
                    "id": "q1",
                    "question": "Las botellas de plástico deben enjuagarse antes de reciclarlas",
                    "correct": True,
                    "explanation": "VERDADERO. Los residuos de líquidos pueden contaminar otros materiales reciclables y atraer plagas en las plantas de reciclaje."
                },
                {
                    "id": "q2",
                    "question": "El papel con manchas de grasa se puede reciclar normalmente",
                    "correct": False,
                    "explanation": "FALSO. La grasa contamina el proceso de reciclaje del papel. El papel sucio debe ir a residuos generales."
                },
                {
                    "id": "q3",
                    "question": "Las cajas de pizza limpias son 100% reciclables",
                    "correct": True,
                    "explanation": "VERDADERO. Si la caja está limpia (sin grasa), es cartón reciclable. Solo las partes con grasa van a residuos generales."
                },
                {
                    "id": "q4",
                    "question": "Todas las botellas de vidrio pueden ir juntas al reciclaje",
                    "correct": False,
                    "explanation": "FALSO. El vidrio de ventanas, espejos y bombillas tiene diferente composición química y debe separarse del vidrio de botellas."
                },
                {
                    "id": "q5",
                    "question": "Las latas de aluminio pueden reciclarse infinitas veces sin perder calidad",
                    "correct": True,
                    "explanation": "VERDADERO. El aluminio es uno de los pocos materiales que puede reciclarse infinitamente sin degradación, ahorrando 95% de energía."
                },
                {
                    "id": "q6",
                    "question": "Los vasos de café desechables son de papel y son totalmente reciclables",
                    "correct": False,
                    "explanation": "FALSO. Tienen una capa de plástico o cera por dentro que impide su reciclaje. Solo la tapa plástica es reciclable."
                },
                {
                    "id": "q7",
                    "question": "El cartón mojado pierde su capacidad de ser reciclado",
                    "correct": True,
                    "explanation": "VERDADERO. El agua debilita las fibras del cartón, haciendo que pierda calidad y sea más difícil de reciclar."
                },
                {
                    "id": "q8",
                    "question": "Los envases Tetra Pak son 100% papel reciclable",
                    "correct": False,
                    "explanation": "FALSO. Están hechos de 6 capas: papel, plástico y aluminio. Requieren un proceso especial de separación para reciclarse."
                }
            ],
            "intermedio": [
                {
                    "id": "q9",
                    "question": "El plástico negro no se puede reciclar debido a los sensores ópticos",
                    "correct": True,
                    "explanation": "VERDADERO. Los sensores infrarrojos en las plantas de reciclaje no detectan el plástico negro, por lo que termina en residuos generales."
                },
                {
                    "id": "q10",
                    "question": "Las bolsas de plástico biodegradables se descomponen en 3 meses",
                    "correct": False,
                    "explanation": "FALSO. Necesitan condiciones industriales específicas (calor, humedad, microorganismos) y pueden tardar años en ambientes naturales."
                },
                {
                    "id": "q11",
                    "question": "Reciclar una tonelada de papel salva aproximadamente 17 árboles",
                    "correct": True,
                    "explanation": "VERDADERO. Además ahorra 26,000 litros de agua y reduce las emisiones de gases de efecto invernadero."
                },
                {
                    "id": "q12",
                    "question": "Los recibos térmicos son papel normal y pueden reciclarse",
                    "correct": False,
                    "explanation": "FALSO. Contienen BPA (Bisfenol A), un químico que contamina el reciclaje de papel. Deben ir a residuos generales."
                },
                {
                    "id": "q13",
                    "question": "El papel de aluminio con restos de comida se puede reciclar si se lava",
                    "correct": True,
                    "explanation": "VERDADERO. El aluminio es altamente reciclable. Si lo lavas y haces una bola grande, facilitarás su detección en la planta."
                },
                {
                    "id": "q14",
                    "question": "Las pajitas de papel son siempre más ecológicas que las de plástico",
                    "correct": False,
                    "explanation": "FALSO. Aunque biodegradables, su producción consume más energía y agua. Las pajitas reutilizables son la mejor opción."
                },
                {
                    "id": "q15",
                    "question": "Los CD y DVD son reciclables en el contenedor de plástico",
                    "correct": False,
                    "explanation": "FALSO. Están hechos de policarbonato con capas metálicas. Requieren reciclaje especializado en puntos limpios."
                },
                {
                    "id": "q16",
                    "question": "Las servilletas y papel higiénico usados pueden compostarse",
                    "correct": False,
                    "explanation": "FALSO. Aunque son biodegradables, pueden contener patógenos. Van a residuos generales, no a compost doméstico."
                }
            ],
            "avanzado": [
                {
                    "id": "q17",
                    "question": "El plástico reciclado tiene la misma calidad que el plástico virgen",
                    "correct": False,
                    "explanation": "FALSO. Cada ciclo de reciclaje degrada las cadenas poliméricas, reduciendo propiedades. Por eso se mezcla con plástico virgen."
                },
                {
                    "id": "q18",
                    "question": "Los microplásticos pueden eliminarse completamente del agua con filtros domésticos",
                    "correct": False,
                    "explanation": "FALSO. Los microplásticos (<5mm) requieren filtración especializada. Los filtros domésticos solo eliminan partículas más grandes."
                },
                {
                    "id": "q19",
                    "question": "Reciclar envases de aerosol es peligroso por riesgo de explosión",
                    "correct": False,
                    "explanation": "FALSO. Si están completamente vacíos (no hacen ruido al agitarse), son seguros. Van al contenedor de metales/plásticos."
                },
                {
                    "id": "q20",
                    "question": "El reciclaje químico puede convertir plástico mezclado en materiales de calidad original",
                    "correct": True,
                    "explanation": "VERDADERO. Descompone polímeros a nivel molecular, permitiendo crear plástico nuevo. Es más costoso que el reciclaje mecánico tradicional."
                },
                {
                    "id": "q21",
                    "question": "Los envases de cartón con ventana de plástico no son reciclables",
                    "correct": False,
                    "explanation": "FALSO. Las plantas modernas pueden separar el plástico del papel. Si la ventana es <50% del envase, es reciclable."
                },
                {
                    "id": "q22",
                    "question": "Las mascarillas quirúrgicas desechables son biodegradables",
                    "correct": False,
                    "explanation": "FALSO. Están hechas de polipropileno (plástico) y pueden tardar hasta 450 años en descomponerse. Van a residuos generales."
                },
                {
                    "id": "q23",
                    "question": "Los aparatos electrónicos contienen oro reciclable",
                    "correct": True,
                    "explanation": "VERDADERO. Una tonelada de celulares contiene más oro que una tonelada de mineral. También tienen plata, cobre y paladio."
                },
                {
                    "id": "q24",
                    "question": "El 'downcycling' es cuando un material reciclado tiene menor calidad que el original",
                    "correct": True,
                    "explanation": "VERDADERO. Opuesto al 'upcycling'. Ej: botellas PET → fibra textil (menor calidad). Es lo más común en reciclaje de plásticos."
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
