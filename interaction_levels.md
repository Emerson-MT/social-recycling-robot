Documento de Niveles de Interacción - Robot Social de Reciclaje
1. Arquitectura General del Sistema
1.1 Flujo de Decisión Inicial
El sistema comienza con un Puntaje de Propensión a la Interacción (PPI) que determina si el usuario recibirá una interacción completa o una retroalimentación mínima.
PPI = f(tiempo_proximidad, historial_usuario, hora_del_día, contexto_ambiental)

Umbral de Interacción: PPI >= 0.6
Factores que influyen en el PPI:

Tiempo de proximidad antes de depositar: >3 segundos sugiere exploración
Historial del usuario: Usuarios recurrentes tienen mayor PPI base
Hora del día: Menor umbral en horarios de bajo tráfico
Contexto ambiental: Ruido ambiente, cantidad de personas cerca


2. Tipos de Usuario y Rutas de Interacción
2.1 Usuario Pragmático (PPI < Umbral)
Perfil: Depositó el residuo y se retira inmediatamente.
Respuesta del Robot:

✅ Luz verde en el contenedor correcto
🔊 Sonido sutil de confirmación (200ms, tono agradable)
🤖 Gesto mínimo del robot (asentimiento leve)
⏱️ Duración total: <1 segundo

Objetivo: No interrumpir, solo confirmar que la acción fue correcta.

2.2 Usuario Explorador (PPI >= Umbral)
Perfil: Permanece cerca del robot después de depositar.
Respuesta del Robot: Compromiso Educativo Progresivo (4 niveles)

3. Niveles de Interacción Detallados
NIVEL 1: Retroalimentación Directa y Relevante
Activación

Usuario deposita residuo
PPI >= Umbral de Interacción
Duración estimada: 3-5 segundos

Implementación
Caso 1: Clasificación Correcta
🎙️ VOZ: "¡Genial! Esa botella de plástico va justo en el contenedor azul."

📺 PANTALLA:
┌─────────────────────────────────┐
│  ✓ ¡Correcto!                   │
│  🍼 Botella PET → 🔵 Azul       │
│  Se convertirá en ropa nueva    │
└─────────────────────────────────┘

💡 EFECTO VISUAL: Animación de botella transformándose
Caso 2: Clasificación Incorrecta
🎙️ VOZ: "¡No te preocupes! Yo lo arreglo. Las servilletas de papel 
usadas van con los residuos generales. ¿Sabías que una sola 
servilleta con grasa puede contaminar miles de litros de papel 
reciclado?"

📺 PANTALLA:
┌─────────────────────────────────┐
│  ℹ️ Te ayudo con eso             │
│  🧻 Servilleta → ⚫ General      │
│  ❌ NO va en papel (tiene grasa)│
│  💡 1 servilleta = 1000L papel  │
│     contaminado                  │
└─────────────────────────────────┘

🤖 GESTO: Robot mueve el residuo al contenedor correcto
Sensor de Permanencia
javascriptif (tiempo_usuario_cerca > 2_segundos) {
    avanzar_a_nivel_2();
} else {
    finalizar_interaccion();
}

NIVEL 2: Desafío Cognitivo (Gamificación)
Activación

Usuario permanece >2 segundos después del Nivel 1
Duración estimada: 10-15 segundos

Implementación
🎙️ VOZ: "Pareces alguien interesado en el reciclaje. 
¡Una pregunta rápida!"

📺 PANTALLA:
┌─────────────────────────────────┐
│  🎮 DESAFÍO RÁPIDO              │
│                                  │
│  ¿Dónde va una caja de pizza    │
│  con manchas de grasa?           │
│                                  │
│  [A] 🟢 Orgánico                │
│  [B] 🔵 Papel                   │
│  [C] ⚫ General                 │
│                                  │
│  ⏱️ 10 segundos                  │
└─────────────────────────────────┘
Mecánica del Juego
Interfaz táctil o por voz:

Usuario selecciona opción A, B o C
Temporizador visible de 10 segundos

Respuesta Correcta (C: General):
🎙️ VOZ: "¡Correcto! La grasa contamina el reciclaje de papel."

📺 PANTALLA:
┌─────────────────────────────────┐
│  ✓ ¡CORRECTO! +10 puntos        │
│  🍕 Pizza con grasa → ⚫ General│
│  💡 Limpia = Papel              │
│     Con grasa = General          │
│  Racha: ⭐⭐⭐ (3 seguidas)     │
└─────────────────────────────────┘
Respuesta Incorrecta:
🎙️ VOZ: "¡Buen intento! La grasa hace que vaya a residuos generales."

📺 PANTALLA:
┌─────────────────────────────────┐
│  ℹ️ Casi... +5 puntos           │
│  Respuesta correcta: ⚫ General │
│  🧠 Regla de oro: Con grasa,   │
│     NO va a papel ni orgánico   │
└─────────────────────────────────┘
Banco de Preguntas por Dificultad
Nivel Básico (primeras 5 interacciones):

Caja de pizza con grasa
Botella de vidrio
Lata de aluminio

Nivel Intermedio (6-15 interacciones):

Envase Tetra Pak
Bombilla LED
Espejo roto

Nivel Avanzado (15+ interacciones):

Máscara quirúrgica
Cepillo de dientes eléctrico
Envase de aerosol

Sensor de Permanencia
javascriptif (usuario_sigue_atento && tiempo_desde_respuesta < 3_segundos) {
    avanzar_a_nivel_3();
} else {
    finalizar_interaccion();
}

NIVEL 3: Conexión Personalizada y Estadística
Activación

Usuario completa Nivel 2 y permanece atento
Duración estimada: 8-12 segundos

Implementación
🎙️ VOZ: "Gracias a tu acción de reciclar esa botella, se ahorra 
la energía suficiente para iluminar el parque que ves al frente 
durante 15 minutos."

📺 PANTALLA:
┌─────────────────────────────────┐
│  🌍 TU IMPACTO HOY              │
│                                  │
│  1 botella = ⚡ 15 min de luz   │
│  en el Parque Kennedy            │
│                                  │
│  📊 TU IMPACTO TOTAL:           │
│  • 47 botellas recicladas        │
│  • ⚡ 11.75 horas de energía    │
│  • 🌳 Equivale a plantar 2      │
│    árboles al año                │
│                                  │
│  Top 12% en tu distrito 🏆      │
└─────────────────────────────────┘
Base de Datos de Equivalencias Locales
javascriptconst equivalencias = {
  botella_PET: {
    energia: "15 min iluminación Parque [NOMBRE_LOCAL]",
    agua: "2 litros ahorrados",
    co2: "50g CO2 evitados"
  },
  lata_aluminio: {
    energia: "3 horas de TV",
    recursos: "95% menos energía vs nueva lata",
    co2: "9kg CO2 evitados"
  },
  carton_1kg: {
    agua: "50 litros ahorrados",
    arboles: "17 árboles salvados por tonelada",
    energia: "50% menos energía vs nuevo"
  }
};
Personalización Geográfica

Detectar ubicación del robot: GPS o configuración manual
Referenciar lugares locales conocidos: Parques, plazas, edificios emblemáticos
Ejemplo Lima: "Parque Kennedy", "Costa Verde", "Estadio Nacional"
Ejemplo Bogotá: "Parque Simón Bolívar", "Cerro de Monserrate"

Sensor de Permanencia
javascriptif (usuario_permanece && (escaneo_QR_posible || usuario_recurrente)) {
    avanzar_a_nivel_4();
} else {
    finalizar_interaccion();
}

NIVEL 4: Cierre con Recompensa y Llamado a la Acción
Activación

Usuario completa Nivel 3 con alta atención
Duración estimada: 10-15 segundos

Implementación
🎙️ VOZ: "¡Eres un campeón del reciclaje! Escanea este código QR 
para obtener 20 Eco-Puntos en nuestra app y compite con tus amigos."

📺 PANTALLA:
┌─────────────────────────────────┐
│  🏆 ¡FELICITACIONES!            │
│                                  │
│  Obtén tu recompensa:            │
│                                  │
│      ┌─────────────┐            │
│      │  QR CODE    │            │
│      │  [████████] │            │
│      │  [████████] │            │
│      └─────────────┘            │
│                                  │
│  🎁 +20 Eco-Puntos              │
│  🏅 Logro desbloqueado:         │
│     "Reciclador Consciente"     │
│                                  │
│  📱 Descarga la app en:         │
│     ecorobot.app/descarga        │
└─────────────────────────────────┘
Sistema de Recompensas
Eco-Puntos:

Acción de reciclaje correcta: +5 puntos
Completar desafío: +10 puntos
Llegar a Nivel 4: +20 puntos bonus
Racha de 7 días consecutivos: +50 puntos

Logros Desbloqueables:
javascriptconst logros = [
  {
    id: "aprendiz_verde",
    nombre: "Aprendiz Verde",
    descripcion: "10 reciclajes correctos",
    icono: "🥉",
    puntos: 50
  },
  {
    id: "guardian_eco",
    nombre: "Guardián Eco",
    descripcion: "50 reciclajes + 80% acierto en desafíos",
    icono: "🥈",
    puntos: 200
  },
  {
    id: "leyenda_planeta",
    nombre: "Leyenda del Planeta",
    descripcion: "200 reciclajes + ayudar a 5 amigos",
    icono: "🥇",
    puntos: 500
  },
  {
    id: "perfeccionista",
    nombre: "Perfeccionista",
    descripcion: "20 reciclajes perfectos seguidos",
    icono: "💎",
    puntos: 300
  }
];
Recompensas Tangibles (opcional):

100 puntos = Descuento 10% en cafeterías aliadas
500 puntos = Entrada gratis a museo ambiental
1000 puntos = Kit de reciclaje para el hogar

QR Code Dinámico
URL estructura:
https://ecorobot.app/r/{user_id}/{interaction_id}/{points}

Ejemplo:
https://ecorobot.app/r/a7f3k/int_20251005_1430/20
Competencia Social
📺 PANTALLA ALTERNATIVA (usuarios avanzados):
┌─────────────────────────────────┐
│  🏆 RANKING SEMANAL             │
│                                  │
│  Tu posición: #8 de 342         │
│  Top 3% en Miraflores 🌟        │
│                                  │
│  🥇 EcoWarrior - 1,240 pts      │
│  🥈 GreenHero - 1,180 pts       │
│  🥉 PlanetSaver - 1,050 pts     │
│  ...                             │
│  8️⃣ Tú - 890 pts               │
│                                  │
│  💪 ¡Solo 160 pts para el Top 5!│
└─────────────────────────────────┘

4. Tabla de Sensores y Umbrales
TransiciónSensorUmbralAlternativa si fallaInicio → Nivel 1PPI>= 0.6Retroalimentación AmbientalNivel 1 → Nivel 2Permanencia> 2 segundosFin de interacciónNivel 2 → Nivel 3Atención + RespuestaResponde + permanece 3sFin de interacciónNivel 3 → Nivel 4Permanencia + EngagementPermanece + historial positivoFin de interacción

5. Gestión de Usuarios Recurrentes
5.1 Identificación (opcional)

Método 1: Reconocimiento facial (con consentimiento)
Método 2: Escaneo de QR en app personal
Método 3: ID anónimo (hash de teléfono)

5.2 Adaptación del Contenido
Usuario Novato (1-5 interacciones):

Preguntas básicas
Explicaciones detalladas
Umbral bajo para avanzar niveles

Usuario Regular (6-20 interacciones):

Preguntas intermedias
Datos de impacto acumulativo
Recordatorios de logros previos

Usuario Experto (20+ interacciones):

Preguntas avanzadas
Comparativas con otros usuarios
Invitaciones a ser "embajador del reciclaje"

5.3 Prevención de Fatiga
javascript// No repetir el mismo mensaje si el usuario vino hace <24 horas
if (ultima_interaccion < 24_horas) {
    usar_variante_mensaje();
    reducir_duracion_niveles();
}

// Rotar banco de preguntas
if (pregunta_ya_respondida) {
    seleccionar_nueva_pregunta();
}

6. Casos Especiales
6.1 Múltiples Usuarios Simultáneos
Si detecta >1 persona:
  - Aumentar volumen de voz
  - Pantalla visible desde múltiples ángulos
  - Nivel 2: Convertir en desafío grupal
  - Nivel 4: QR múltiples (uno por persona)
6.2 Niños (detectado por altura o voz)
- Voz más animada
- Vocabulario simplificado
- Animaciones más coloridas
- Preguntas adaptadas: "¿De qué color es el contenedor de plástico?"
6.3 Hora de Alto Tráfico
Si (hora_pico && cola_de_usuarios > 3):
  - Reducir Nivel 1 a 2 segundos
  - Saltear Nivel 2 (gamificación)
  - Ofrecer Nivel 4 inmediatamente con frase:
    "¡Veo que hay prisa! Escanea el QR para jugar después"

7. Métricas de Éxito
KPIs por Nivel
MétricaObjetivoHerramienta% usuarios que llegan a Nivel 2>40%Sensor de permanencia% usuarios que completan Nivel 2>60%Tasa de respuesta% usuarios que escanean QR>25%Analytics del QRTiempo promedio de interacción15-30sTimer internoTasa de reciclaje correcto>85%Sistema de clasificación
Dashboard de Monitoreo
Datos a recopilar (anónimos):
- Hora de interacción
- Duración por nivel
- Tipo de residuo depositado
- Correcto/Incorrecto
- Nivel alcanzado
- QR escaneado (sí/no)
- Ubicación del robot

8. Pseudocódigo de Implementación
pythonclass RobotReciclaje:
    def __init__(self):
        self.estado = "ESPERA"
        self.usuario_actual = None
        
    def loop_principal(self):
        while True:
            if sensor_proximidad.detecta_usuario():
                self.usuario_actual = self.identificar_usuario()
                ppi = self.calcular_ppi(self.usuario_actual)
                
                # Esperar a que deposite residuo
                residuo = self.esperar_deposito()
                self.clasificar_residuo(residuo)
                
                if ppi >= UMBRAL_INTERACCION:
                    self.iniciar_compromiso_educativo()
                else:
                    self.retroalimentacion_ambiental()
                    
                self.estado = "ESPERA"
    
    def iniciar_compromiso_educativo(self):
        # NIVEL 1
        self.nivel_1_retroalimentacion()
        if not self.sensor_permanencia(duracion=2):
            return
        
        # NIVEL 2
        self.nivel_2_desafio()
        if not self.sensor_atencion():
            return
        
        # NIVEL 3
        self.nivel_3_impacto_personalizado()
        if not self.sensor_permanencia(duracion=3):
            return
        
        # NIVEL 4
        self.nivel_4_recompensa_qr()
    
    def calcular_ppi(self, usuario):
        """
        PPI = Puntaje de Propensión a la Interacción
        Rango: 0.0 - 1.0
        """
        base = 0.5
        
        # Factor histórico
        if usuario.interacciones > 10:
            base += 0.2
        elif usuario.interacciones > 3:
            base += 0.1
        
        # Factor de tiempo de aproximación
        if self.tiempo_proximidad > 5:
            base += 0.15
        
        # Factor de hora del día
        if self.es_hora_baja_demanda():
            base += 0.1
        
        # Factor de éxito previo
        if usuario.tasa_acierto > 0.8:
            base += 0.05
        
        return min(base, 1.0)

9. Consideraciones de Diseño UX/UI
9.1 Pantalla

Tamaño mínimo: 10" táctil
Brillo: Auto-ajustable según luz ambiente
Altura: 1.2m - 1.5m (accesible para niños y adultos)
Tipografía: Sans-serif, mínimo 24pt

9.2 Audio

Volumen: 60-75 dB (ajustable según ruido ambiente)
Voz: Amigable, neutral en género, velocidad moderada
Idiomas: Español (prioritario) + opción de inglés

9.3 Gestos del Robot

Asentimiento: Movimiento sutil de cabeza (1-2cm)
Señalización: Brazo apunta al contenedor correcto
Celebración: Pequeño "baile" al completar Nivel 4


10. Roadmap de Implementación
Fase 1: MVP (Mínimo Producto Viable)

✅ Nivel 1 completo
✅ Retroalimentación ambiental
✅ Sistema de clasificación básico
✅ Sensor de permanencia

Fase 2: Gamificación

✅ Nivel 2 con 10 preguntas básicas
✅ Sistema de puntuación
✅ Pantalla táctil funcional

Fase 3: Personalización

✅ Nivel 3 con datos locales
✅ Base de datos de usuarios
✅ Equivalencias de impacto

Fase 4: Ecosistema Completo

✅ Nivel 4 con QR y app
✅ Rankings sociales
✅ Recompensas tangibles
✅ Dashboard de analytics


Anexo: Ejemplo Completo de Interacción
Escenario: María, 28 años, tercera vez que usa el robot
[09:45 AM - Parque Kennedy, Lima]

1️⃣ María se acerca con una botella de agua vacía
   PPI calculado: 0.72 (recurrente + hora tranquila)
   
2️⃣ Deposita la botella en el contenedor azul ✓

3️⃣ NIVEL 1 (3 segundos):
   🎙️ "¡Perfecto María! Esa botella PET va directo al azul. 
       Se convertirá en fibra para ropa nueva."
   📺 [Animación: botella → camiseta]
   
4️⃣ María sonríe y se queda mirando...

5️⃣ NIVEL 2 (12 segundos):
   🎙️ "¡Una pregunta rápida! ¿Dónde va un vaso de café 
       desechable con tapa de plástico?"
   📺 [Opciones A/B/C con timer 10s]
   María selecciona: C - Separar (tapa→azul, vaso→general)
   🎙️ "¡Excelente! +10 puntos. Racha: ⭐⭐"
   
6️⃣ María saca su teléfono (sensor detecta posible escaneo QR)

7️⃣ NIVEL 3 (10 segundos):
   🎙️ "Con tus 3 botellas recicladas esta semana, has ahorrado
       energía para iluminar el Parque Kennedy durante 45 minutos."
   📺 [Gráfico: 3 botellas = 45 min ⚡]
       "Estás en el Top 8% de Miraflores 🏆"
   
8️⃣ María asiente entusiasmada

9️⃣ NIVEL 4 (15 segundos):
   🎙️ "¡Eres una leyenda del reciclaje! Escanea para obtener
       20 Eco-Puntos y un cupón de descuento."
   📺 [QR Code grande + Logro desbloqueado: "Guardián Eco"]
   
🔟 María escanea el QR
   Sistema registra: +20 puntos, logro guardado
   
[Fin - 40 segundos totales]