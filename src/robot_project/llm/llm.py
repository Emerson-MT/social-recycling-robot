import openai

class LargeLanguageModel:
    def __init__(self, api_key, api_base, model):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

        openai.api_key = self.api_key
        openai.api_base = self.api_base
        self.client = openai
    
    def ask_llm(self, mensaje):
        try:
            response = self.client.ChatCompletion.create(
                model=self.model["model"],
                messages=[
                    {"role": "system", "content": "Eres un robot social llamado Peri que responde solo sobre reciclaje, residuos, sostenibilidad y medio ambiente. "
                    "Además, tienes una personalidad lúdica y carismática: haces bromas, preguntas curiosas y usas frases como "
                    "'¡genial!', '¡súper ecológico!' y '¡vamos allá!'. "
                    "Responde en frases cortas y concisas, alegre y directa, como si hablaras en voz alta. "
                    "Evita explicaciones largas o detalles técnicos innecesarios."
                    },
                    {"role": "user", "content": mensaje}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ Error al consultar el modelo: {e}"