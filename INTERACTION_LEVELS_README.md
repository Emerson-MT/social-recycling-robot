# Sistema de Niveles de Interacción - Robot Reciclaje Peri

## 📋 Descripción General

Este sistema implementa **interacciones educativas progresivas** basadas en el documento `interaction_levels.md`. El robot adapta su comportamiento según el nivel de interés del usuario, ofreciendo desde retroalimentación mínima hasta experiencias educativas completas con gamificación e impacto personalizado.

## 🎯 MVP Implementado (Niveles 1-3)

### **Nivel 1: Retroalimentación Directa**
- ✅ Clasificación de residuo con feedback visual y auditivo
- ✅ Información educativa sobre reciclaje
- ✅ Sensor de permanencia para avanzar a Nivel 2

### **Nivel 2: Gamificación**
- ✅ Banco de preguntas adaptadas al nivel del usuario
- ✅ Sistema de puntos y rachas
- ✅ Retroalimentación educativa en respuestas
- ✅ Sensor de atención para avanzar a Nivel 3

### **Nivel 3: Impacto Personalizado**
- ✅ Cálculo de impacto ambiental local
- ✅ Estadísticas acumuladas del usuario
- ✅ Sistema de logros desbloqueables
- ✅ Rankings y comparativas

## 🚀 Cómo Usar

### **Modo Niveles de Interacción (Por defecto)**

```bash
python main.py
```

El sistema usará automáticamente el modo de niveles si:
- No hay variable de entorno `ROBOT_LEGACY_MODE=true`
- Estás en modo mock (desarrollo local)

### **Modo Legacy (Antiguo)**

Para usar el sistema antiguo:

```bash
export ROBOT_LEGACY_MODE=true
python main.py
```

O en Windows PowerShell:
```powershell
$env:ROBOT_LEGACY_MODE="true"
python main.py
```

### **Modo Mock (Desarrollo)**

El modo mock se activa automáticamente cuando NO estás en Raspberry Pi. También puedes forzarlo:

```bash
export ROBOT_MOCK_MODE=true
python main.py
```

## ⚙️ Configuración

### **config.json**

```json
{
  "interaction_levels": {
    "enabled": true,
    "ppi_threshold": 0.6,
    "level_1": {
      "duration_seconds": 5
    },
    "level_2": {
      "permanence_threshold_seconds": 2,
      "quiz_timer_seconds": 10,
      "points_correct": 10,
      "points_attempt": 5
    },
    "level_3": {
      "permanence_threshold_seconds": 3,
      "location": "Lima",
      "district": "Miraflores"
    }
  }
}
```

### **Parámetros Configurables**

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `ppi_threshold` | Umbral de PPI para activar niveles educativos | 0.6 |
| `level_2.permanence_threshold_seconds` | Segundos de permanencia para Nivel 2 | 2 |
| `level_2.quiz_timer_seconds` | Tiempo para responder quiz | 10 |
| `level_2.points_correct` | Puntos por respuesta correcta | 10 |
| `level_2.points_attempt` | Puntos por intento | 5 |
| `level_3.location` | Ciudad para referencias locales | "Lima" |
| `level_3.district` | Distrito para rankings | "Miraflores" |

## 🧩 Arquitectura del Sistema

### **Componentes Principales**

```
src/robot_project/
├── robot/
│   ├── interaction_levels_fsm.py    # FSM con niveles 1-3
│   └── recycling_robot.py           # Robot principal con selector de modo
├── sensors/
│   └── mock_proximity_sensor.py     # Sensor de proximidad (mock)
├── display/
│   └── mock_display.py              # Pantalla táctil (mock)
├── gamification/
│   └── quiz_system.py               # Sistema de quizzes y logros
├── analytics/
│   └── impact_calculator.py         # Calculadora de impacto ambiental
├── database/
│   └── mock_database.py             # BD extendida con historial
└── configs/
    ├── config.json                  # Configuración de niveles
    └── environment.py               # Detección de modo
```

### **Flujo de Decisión**

```
Usuario detectado
    ↓
Medir tiempo aproximación + obtener historial
    ↓
Calcular PPI (Puntaje de Propensión a Interacción)
    ↓
PPI >= 0.6?
    ↓                           ↓
   SÍ                          NO
    ↓                           ↓
NIVEL 1                    Retroalimentación
(Feedback educativo)       Mínima (< 1s)
    ↓
¿Usuario permanece 2s?
    ↓ SÍ
NIVEL 2
(Quiz gamificado)
    ↓
¿Usuario atento y permanece 3s?
    ↓ SÍ
NIVEL 3
(Impacto personalizado + logros)
```

## 📊 Cálculo de PPI (Simplificado)

El **Puntaje de Propensión a Interacción** se calcula basado en:

```python
PPI = base (0.5)
    + factor_historial (0.0 - 0.2)
    + factor_aproximacion (0.0 - 0.15)
    + factor_acierto (0.0 - 0.05)
```

**Factores:**
- **Historial**: +0.2 si > 10 interacciones, +0.1 si > 3
- **Aproximación**: +0.15 si > 3 segundos, +0.05 si > 1 segundo
- **Acierto**: +0.05 si tasa de acierto en quizzes > 80%

## 🎮 Sistema de Gamificación

### **Banco de Preguntas**

Las preguntas se adaptan según nivel del usuario:

| Nivel | Interacciones | Ejemplo |
|-------|---------------|---------|
| Básico | 0-5 | "¿Dónde va una botella de plástico?" |
| Intermedio | 6-15 | "¿Dónde va un envase Tetra Pak?" |
| Avanzado | 15+ | "¿Dónde va una mascarilla quirúrgica?" |

### **Sistema de Puntos**

- Respuesta correcta: **10 puntos**
- Intento incorrecto: **5 puntos**
- Racha de 3 correctas: ⭐⭐⭐ bonus visual
- Nivel 3 completado: **20 puntos bonus**

### **Logros Desbloqueables**

| Logro | Requisito | Puntos |
|-------|-----------|--------|
| 🥉 Aprendiz Verde | 10 reciclajes correctos | 50 |
| 🥈 Guardián Eco | 50 reciclajes + 80% acierto | 200 |
| 💎 Perfeccionista | 10 reciclajes perfectos seguidos | 300 |
| 🌟 Reciclador Consciente | Completar Nivel 3 | 20 |

## 🌍 Cálculo de Impacto Ambiental

### **Equivalencias por Residuo**

| Tipo | Energía | Agua | CO₂ |
|------|---------|------|-----|
| Plástico (1 item) | 15 min luz | 2 L | 50g |
| Papel (1 item) | 10 min luz | 50 L | 30g |
| Cartón (1 item) | 12 min luz | 50 L | 35g |

### **Referencias Locales**

El sistema personaliza los mensajes según ubicación:

**Lima:**
- "Energía para iluminar Parque Kennedy durante 15 minutos"
- "Ranking: Top 12% en Miraflores 🏆"

**Bogotá:**
- "Energía para iluminar Parque Simón Bolívar..."

## 🗄️ Base de Datos Extendida

### **Nuevos Campos de Usuario**

```python
{
    "student_code": 12345678,
    "student_name": "Juan Pérez",
    "student_points": 10,
    "total_interactions": 3,           # NUEVO
    "correct_recycles": 2,             # NUEVO
    "quiz_correct": 1,                 # NUEVO
    "quiz_total": 2,                   # NUEVO
    "perfect_streak": 0,               # NUEVO
    "current_streak": 0,               # NUEVO
    "unlocked_achievements": set(),    # NUEVO
    "recycling_history": {             # NUEVO
        "plastico": 1,
        "papel": 1,
        "carton": 0,
        "residuo_general": 0
    },
    "last_interaction": None,          # NUEVO
    "reached_level_3": False           # NUEVO
}
```

### **Nuevos Métodos de BD**

```python
# Obtener estadísticas completas
db.get_student_stats(student_code)

# Actualizar estadísticas de reciclaje
db.update_recycling_stats(student_code, waste_type, is_correct)

# Actualizar estadísticas de quiz
db.update_quiz_stats(student_code, is_correct, points_earned)

# Desbloquear logro
db.unlock_achievement(student_code, achievement_id)

# Marcar nivel alcanzado
db.mark_level_reached(student_code, level)
```

## 🧪 Pruebas en Modo Mock

### **Códigos de Estudiante de Prueba**

| Código | Nombre | Interacciones | Nivel |
|--------|--------|---------------|-------|
| 12345678 | Juan Pérez | 3 | Novato |
| 87654321 | María García | 8 | Regular |
| 33333333 | Carlos Rodríguez | 12 | Experto |

### **Simulación de Sensores**

El modo mock te preguntará interactivamente:

```
🤖 [SENSOR] ¿El usuario permanece cerca del robot por al menos 2 segundos?
   [s] Sí, permanece
   [n] No, se retira
```

```
🤖 [SENSOR] ¿Cuánto tiempo estuvo el usuario cerca antes de depositar?
   [1] < 1 segundo (rápido)
   [2] 1-3 segundos (normal)
   [3] > 3 segundos (explorando)
```

## 🔧 Troubleshooting

### **El sistema no usa niveles de interacción**

Verifica:
```bash
# Debe imprimir: False (o vacío)
echo $ROBOT_LEGACY_MODE

# Si está en "true", desactívalo
unset ROBOT_LEGACY_MODE
```

### **Errores de importación**

Asegúrate de tener instaladas las dependencias:
```bash
pip install -r requirements.txt
```

### **Base de datos no actualiza**

En modo mock, los cambios son en memoria. Verifica que estés usando el mismo código de estudiante:
```python
# Códigos válidos en mock
[12345678, 87654321, 11111111, 22222222, 33333333]
```

## 📈 Próximas Mejoras (Nivel 4)

- [ ] Generación de códigos QR dinámicos
- [ ] Integración con app móvil
- [ ] Rankings sociales en tiempo real
- [ ] Recompensas tangibles (cupones, descuentos)
- [ ] Detección de múltiples usuarios simultáneos
- [ ] Adaptación para niños (altura/voz)

## 🤝 Contribuir

Para agregar nuevas preguntas al banco:

1. Edita `src/robot_project/gamification/quiz_system.py`
2. Agrega preguntas en el nivel correspondiente (básico/intermedio/avanzado)
3. Usa el formato:
```python
{
    "id": "q_unique_id",
    "question": "Texto de la pregunta",
    "options": [
        {"key": "A", "text": "Opción 1", "icon": "emoji"},
        {"key": "B", "text": "Opción 2", "icon": "emoji"},
        {"key": "C", "text": "Opción 3", "icon": "emoji"}
    ],
    "correct": "A",
    "explanation": "Explicación educativa"
}
```

## 📚 Referencias

- Documento original: [interaction_levels.md](interaction_levels.md)
- Guía del proyecto: [CLAUDE.md](CLAUDE.md)
- Configuración: [config.json](src/robot_project/configs/config.json)

---

**Desarrollado con ❤️ para el proyecto Robot Social de Reciclaje "Peri"**
