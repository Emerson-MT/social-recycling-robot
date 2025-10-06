import time
import random
from datetime import datetime

class MockStudentDatabase:
    """Simulación de base de datos para desarrollo sin MySQL"""

    def __init__(self, config):
        self.config = config
        # Base de datos simulada en memoria con historial extendido
        self.students = {
            12345678: {
                "student_name": "Juan Pérez",
                "student_points": 10,
                "total_interactions": 3,
                "correct_recycles": 2,
                "quiz_correct": 1,
                "quiz_total": 2,
                "perfect_streak": 0,
                "current_streak": 0,
                "unlocked_achievements": set(),
                "recycling_history": {"plastico": 1, "papel": 1, "carton": 0, "residuo_general": 0},
                "last_interaction": None,
                "reached_level_3": False
            },
            87654321: {
                "student_name": "María García",
                "student_points": 25,
                "total_interactions": 8,
                "correct_recycles": 6,
                "quiz_correct": 5,
                "quiz_total": 6,
                "perfect_streak": 3,
                "current_streak": 3,
                "unlocked_achievements": {"aprendiz_verde"},
                "recycling_history": {"plastico": 3, "papel": 2, "carton": 1, "residuo_general": 0},
                "last_interaction": None,
                "reached_level_3": True
            },
            11111111: {
                "student_name": "Pedro López",
                "student_points": 5,
                "total_interactions": 1,
                "correct_recycles": 1,
                "quiz_correct": 0,
                "quiz_total": 1,
                "perfect_streak": 0,
                "current_streak": 0,
                "unlocked_achievements": set(),
                "recycling_history": {"plastico": 0, "papel": 0, "carton": 1, "residuo_general": 0},
                "last_interaction": None,
                "reached_level_3": False
            },
            22222222: {
                "student_name": "Ana Martínez",
                "student_points": 15,
                "total_interactions": 5,
                "correct_recycles": 4,
                "quiz_correct": 3,
                "quiz_total": 4,
                "perfect_streak": 2,
                "current_streak": 2,
                "unlocked_achievements": set(),
                "recycling_history": {"plastico": 2, "papel": 1, "carton": 1, "residuo_general": 0},
                "last_interaction": None,
                "reached_level_3": False
            },
            33333333: {
                "student_name": "Carlos Rodríguez",
                "student_points": 30,
                "total_interactions": 12,
                "correct_recycles": 10,
                "quiz_correct": 8,
                "quiz_total": 10,
                "perfect_streak": 5,
                "current_streak": 1,
                "unlocked_achievements": {"aprendiz_verde", "perfeccionista"},
                "recycling_history": {"plastico": 4, "papel": 3, "carton": 2, "residuo_general": 1},
                "last_interaction": None,
                "reached_level_3": True
            },
        }
        print(f"🔧 [MOCK] Base de datos simulada con {len(self.students)} estudiantes")
        print(f"🔧 [MOCK] Códigos disponibles: {list(self.students.keys())}")

    def get_connection(self):
        """Simula la obtención de una conexión a la base de datos"""
        print("🔧 [MOCK] Conexión a base de datos simulada")
        time.sleep(0.2)  # Simular latencia
        return "mock_connection"

    def update_student_info(self, student_code, field):
        """
        Simula la actualización de información del estudiante.
        En este caso, incrementa los puntos del estudiante.
        """
        print(f"🔧 [MOCK] Buscando estudiante con código: {student_code}")
        time.sleep(0.3)  # Simular consulta a BD

        if student_code in self.students:
            # Incrementar puntos
            if field == "student_points":
                self.students[student_code]["student_points"] += 1
                print(f"✅ [MOCK] Puntos actualizados para {self.students[student_code]['student_name']}")
                print(f"✅ [MOCK] Nuevos puntos: {self.students[student_code]['student_points']}")
                return True
        else:
            print(f"❌ [MOCK] Código de estudiante {student_code} no encontrado")
            print(f"💡 [MOCK] Códigos válidos: {list(self.students.keys())}")
            return False

    def get_student_info(self, student_code, field):
        """Obtiene información específica de un estudiante"""
        if student_code in self.students:
            value = self.students[student_code].get(field)
            print(f"🔧 [MOCK] Obteniendo {field} para código {student_code}: {value}")
            return value
        return None

    def get_student_stats(self, student_code):
        """Obtiene todas las estadísticas del estudiante"""
        if student_code in self.students:
            stats = self.students[student_code].copy()
            # Calcular tasa de acierto en quizzes
            if stats["quiz_total"] > 0:
                stats["quiz_accuracy"] = stats["quiz_correct"] / stats["quiz_total"]
            else:
                stats["quiz_accuracy"] = 0
            return stats
        return None

    def update_recycling_stats(self, student_code, waste_type, is_correct):
        """Actualiza estadísticas de reciclaje"""
        if student_code in self.students:
            student = self.students[student_code]
            student["total_interactions"] += 1
            student["last_interaction"] = datetime.now()

            if is_correct:
                student["correct_recycles"] += 1
                student["current_streak"] += 1
                if student["current_streak"] > student["perfect_streak"]:
                    student["perfect_streak"] = student["current_streak"]
            else:
                student["current_streak"] = 0

            # Actualizar historial de reciclaje
            if waste_type in student["recycling_history"]:
                student["recycling_history"][waste_type] += 1

            print(f"✅ [MOCK] Estadísticas actualizadas para {student['student_name']}")
            return True
        return False

    def update_quiz_stats(self, student_code, is_correct, points_earned):
        """Actualiza estadísticas de quiz"""
        if student_code in self.students:
            student = self.students[student_code]
            student["quiz_total"] += 1
            if is_correct:
                student["quiz_correct"] += 1
            student["student_points"] += points_earned
            print(f"✅ [MOCK] Quiz stats actualizadas. Puntos: +{points_earned}")
            return True
        return False

    def unlock_achievement(self, student_code, achievement_id):
        """Desbloquea un logro para el estudiante"""
        if student_code in self.students:
            self.students[student_code]["unlocked_achievements"].add(achievement_id)
            print(f"🏆 [MOCK] Logro desbloqueado: {achievement_id}")
            return True
        return False

    def mark_level_reached(self, student_code, level):
        """Marca que el estudiante alcanzó un nivel específico"""
        if student_code in self.students:
            self.students[student_code][f"reached_level_{level}"] = True
            print(f"✅ [MOCK] Nivel {level} alcanzado por estudiante {student_code}")
            return True
        return False

    def add_student(self, student_code, student_name, student_points=0):
        """Agrega un nuevo estudiante a la base de datos simulada"""
        self.students[student_code] = {
            "student_name": student_name,
            "student_points": student_points,
            "total_interactions": 0,
            "correct_recycles": 0,
            "quiz_correct": 0,
            "quiz_total": 0,
            "perfect_streak": 0,
            "current_streak": 0,
            "unlocked_achievements": set(),
            "recycling_history": {"plastico": 0, "papel": 0, "carton": 0, "residuo_general": 0},
            "last_interaction": None,
            "reached_level_3": False
        }
        print(f"✅ [MOCK] Estudiante agregado: {student_name} ({student_code})")

    def list_all_students(self):
        """Lista todos los estudiantes en la base de datos simulada"""
        print("\n📋 [MOCK] Estudiantes en base de datos:")
        for code, info in self.students.items():
            print(f"  {code}: {info['student_name']} - {info['student_points']} puntos")
        print()
