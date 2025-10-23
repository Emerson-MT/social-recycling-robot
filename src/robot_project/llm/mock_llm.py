import time
import random

class MockLargeLanguageModel:
    """Simulación de LLM para desarrollo sin API real"""

    def __init__(self, api_key, api_base, model):
        self.api_key = "mock_key"
        self.api_base = api_base
        self.model = model
        print(f"🔧 [MOCK] LLM simulado (modelo: {model})")

        # Respuestas predefinidas sobre reciclaje
        self.respuestas_reciclaje = [
            "¡Genial pregunta! El reciclaje ayuda a reducir la contaminación y proteger nuestro planeta. ¡Súper ecológico!",
            "¡Vamos allá! Reciclar es importante porque ahorramos recursos naturales y energía. ¿No te parece increíble?",
            "¡Me encanta tu interés! Separar residuos correctamente ayuda a que se puedan reutilizar materiales. ¡Genial!",
            "¡Súper pregunta! El plástico puede tardar cientos de años en descomponerse, por eso es tan importante reciclarlo.",
            "¡Qué curioso eres! El papel reciclado salva árboles y reduce la energía necesaria para hacer papel nuevo.",
            "¡Excelente! El cartón es uno de los materiales más fáciles de reciclar. ¿Sabías que se puede reciclar hasta 7 veces?",
            "¡Me gusta tu actitud! Cada vez que reciclas, estás haciendo del mundo un lugar mejor. ¡Vamos allá!",
            "¡Genial! El reciclaje reduce los desechos en los vertederos y ayuda a mantener limpio nuestro ambiente.",
            "¡Súper ecológico! Al reciclar, contribuyes a disminuir las emisiones de gases de efecto invernadero.",
            "¡Qué buena onda! Reciclar es una forma sencilla pero poderosa de cuidar nuestro planeta.",
        ]

        self.respuestas_generales = [
            "¡Interesante! Cuéntame más sobre eso.",
            "¡Genial! Me encanta aprender cosas nuevas contigo.",
            "¡Súper! Esa es una buena observación.",
            "¡Vamos allá! Sigamos conversando sobre el medio ambiente.",
            "¡Qué curioso! ¿Te gustaría saber más sobre reciclaje?",
        ]

    def ask_llm(self, mensaje):
        """Simula una consulta al LLM"""
        print(f"🔧 [MOCK] Procesando pregunta: {mensaje}")
        time.sleep(0.8)  # Simular tiempo de respuesta de API

        # Detectar palabras clave relacionadas con reciclaje
        palabras_reciclaje = [
            "recicl", "residuo", "basura", "plástico", "papel", "cartón",
            "medio ambiente", "contaminación", "planeta", "ecológico",
            "sostenible", "reutilizar", "reducir", "separar", "contenedor"
        ]

        mensaje_lower = mensaje.lower()
        es_sobre_reciclaje = any(palabra in mensaje_lower for palabra in palabras_reciclaje)

        if es_sobre_reciclaje:
            respuesta = random.choice(self.respuestas_reciclaje)
        else:
            respuesta = random.choice(self.respuestas_generales)

        print(f"✅ [MOCK] Respuesta generada")
        return respuesta

    def generate_recycling_response(self, waste_type):
        """Genera una respuesta específica para un tipo de residuo"""
        respuestas = {
            "cartón": "¡Genial! El cartón es súper reciclable. Recuerda aplanarlo antes de reciclarlo. ¡Vamos allá!",
            "papel": "¡Súper! El papel es uno de los materiales más reciclados del mundo. ¡Qué ecológico!",
            "plástico": "¡Excelente! El plástico debe reciclarse siempre que sea posible. ¡Salvemos el planeta!",
            "residuo_general": "Hmm, este residuo no es reciclable, pero gracias por separarlo correctamente. ¡Genial!"
        }
        return respuestas.get(waste_type, "¡Súper! Gracias por reciclar conmigo.")
