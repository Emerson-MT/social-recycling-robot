# Ejemplos de Prueba - Modo Desarrollo

Este documento contiene ejemplos detallados de cómo probar cada funcionalidad del robot en modo desarrollo (con mocks).

## 🎯 Datos de Prueba Disponibles

### Estudiantes en la base de datos mock:

| Código | Nombre | Puntos Iniciales |
|--------|--------|------------------|
| 12345678 | Juan Pérez | 10 |
| 87654321 | María García | 25 |
| 11111111 | Pedro López | 5 |
| 22222222 | Ana Martínez | 15 |
| 33333333 | Carlos Rodríguez | 30 |

### Atajos de consola:

| Atajo | Comando Completo |
|-------|------------------|
| r | reciclar |
| y | yo |
| t | tú |
| 0 | cartón |
| 1 | papel |
| 2 | plástico |
| 3 | residuo_general |

---

## 📝 Ejemplo 1: Conversación Simple (Opción 8)

```bash
python main.py
```

**Entrada:**
```
Ingrese el número de la prueba a realizar: 8
```

**Flujo de conversación:**

```
🤖 Robot: Se eligió coversar. Cuentame, estoy aquí para escucharte...

[Comandos disponibles]:
  r: reciclar
  y: yo
  t: tú
  0: cartón
  1: papel
  2: plástico
  3: residuo_general

[Consola] Escribe un comando: por que es importante reciclar
🔧 [MOCK] Procesando pregunta: por que es importante reciclar
✅ [MOCK] Respuesta generada
🤖 Robot: ¡Genial pregunta! El reciclaje ayuda a reducir la contaminación...

[Consola] Escribe un comando: que pasa con el plastico
🔧 [MOCK] Procesando pregunta: que pasa con el plastico
🤖 Robot: ¡Súper pregunta! El plástico puede tardar cientos de años...

[Consola] Escribe un comando: adios
🤖 Robot: Un gusto conversar contigo. Hasta pronto!
```

---

## 📝 Ejemplo 2: Clasificación de Residuo (Opción 4)

```bash
python main.py
```

**Entrada:**
```
Ingrese el número de la prueba a realizar: 4
```

**Salida esperada:**

```
📸 [MOCK] Clasificando residuo (esperando 3s)...
✅ [MOCK] Detectado: plástico (id 2) con confianza 0.87
Resultado final: plástico (id 2) con confianza 0.87

🔊 [MOCK] TTS: Se detectó plástico.
🤖 Robot: Se detectó plástico.

🔊 [MOCK] TTS: Prueba de clasificación finalizada.
🤖 Robot: Prueba de clasificación finalizada.
```

---

## 📝 Ejemplo 3: Sistema de Recompensas (Opción 7)

```bash
python main.py
```

**Entrada:**
```
Ingrese el número de la prueba a realizar: 7
```

**Flujo completo (caso exitoso):**

```
🔊 [MOCK] TTS: Ingrese el residuo detectado
🤖 Robot: Ingrese el residuo detectado

Ingrese el residuo detectado: 2

🔊 [MOCK] TTS: Ahora ingrese el contenedor al que corresponde
🤖 Robot: Ahora ingrese el contenedor al que corresponde

Ingrese el contenedor al que corresponde: 2

🤖 Robot: Muy bien! Te ganaste una recompensa. Por favor díctame tu código.

[Comandos disponibles]:
  ...

[Consola] Escribe un comando: 12345678

🔧 [MOCK] Buscando estudiante con código: 12345678
✅ [MOCK] Puntos actualizados para Juan Pérez
✅ [MOCK] Nuevos puntos: 11
🔧 [MOCK] Obteniendo student_name para código 12345678: Juan Pérez
🔧 [MOCK] Obteniendo student_points para código 12345678: 11

🤖 Robot: Hola Juan! Gracias por ayudar a reciclar. Tus puntos ahora son de 11. Hasta pronto!
```

**Flujo con código inválido:**

```
[Consola] Escribe un comando: 99999999

🔧 [MOCK] Buscando estudiante con código: 99999999
❌ [MOCK] Código de estudiante 99999999 no encontrado
💡 [MOCK] Códigos válidos: [12345678, 87654321, 11111111, 22222222, 33333333]

🤖 Robot: Lo siento, no encontré ese código. Por favor intenta de nuevo.
```

---

## 📝 Ejemplo 4: Programa Completo - FSM (Opción 9)

Este es el ejemplo más completo, simula el flujo completo del robot.

```bash
python main.py
```

**Entrada:**
```
Ingrese el número de la prueba a realizar: 9
```

### Escenario A: Reciclaje Manual con Recompensa

```
🔊 [MOCK] Reproduciendo audio: starting_sound-effect.mp3
🤖 Robot: Hola, soy Peri. Reciclemos juntos!.

[Consola] Escribe un comando: r

🤖 Robot: Genial! Sigue las instrucciones para empezar.

📸 [MOCK] Clasificando residuo (esperando 3s)...
✅ [MOCK] Detectado: papel (id 1) con confianza 0.92

🤖 Robot: Se detectó papel.
📤 [MOCK] Enviando: RESIDUO:1
📥 [MOCK] Esperando mensaje con prefijo: LLENO:
📥 [MOCK] Recibido: LLENO:0
El tacho cuenta con espacio

🤖 Robot: ¿Quieres que lo recicle yo o prefieres hacerlo tú para ganar una recompensa?

[Consola] Escribe un comando: y

🤖 Robot: Presiona el botón correcto según el tipo de residuo.
Esperando que usuario presione botón:

📤 [MOCK] Enviando: SEGRE_AUTO:0
📥 [MOCK] Esperando mensaje con prefijo: BOTON_RES:
📥 [MOCK] Recibido: BOTON_RES:1

# Si el botón coincide con el residuo (ambos son 1 = papel):
🔊 [MOCK] Reproduciendo audio: winning_sound-effect.mp3
🤖 Robot: Bien hecho! Ganaste una recompensa. ¿Cuál es tu código?

[Consola] Escribe un comando: 87654321

🔧 [MOCK] Buscando estudiante con código: 87654321
✅ [MOCK] Puntos actualizados para María García
✅ [MOCK] Nuevos puntos: 26

🤖 Robot: Hola María! Gracias por ayudar a reciclar. Tus puntos ahora son de 26. Hasta pronto!

# Vuelve al estado INICIO
🔊 [MOCK] Reproduciendo audio: starting_sound-effect.mp3
🤖 Robot: Hola, soy Peri. Reciclemos juntos!.
```

### Escenario B: Reciclaje Automático

```
[Consola] Escribe un comando: r

🤖 Robot: Genial! Sigue las instrucciones para empezar.

📸 [MOCK] Clasificando residuo (esperando 3s)...
✅ [MOCK] Detectado: cartón (id 0) con confianza 0.95

🤖 Robot: Se detectó cartón.
🤖 Robot: ¿Quieres que lo recicle yo o prefieres hacerlo tú para ganar una recompensa?

[Consola] Escribe un comando: t

🤖 Robot: Listo! Yo me encargo.
📤 [MOCK] Enviando: SEGRE_AUTO:1
🤖 Robot: Gracias por reciclar! Hasta pronto!

# Vuelve al estado INICIO
```

### Escenario C: Conversación

```
[Consola] Escribe un comando: conversar

🤖 Robot: Hablemos! Puedes decir adiós cuando quieras terminar.

[Consola] Escribe un comando: como puedo ayudar al medio ambiente

🔧 [MOCK] Procesando pregunta: como puedo ayudar al medio ambiente
✅ [MOCK] Respuesta generada
🤖 Robot: ¡Vamos allá! Reciclar es importante porque ahorramos recursos...

[Consola] Escribe un comando: que es el plastico

🔧 [MOCK] Procesando pregunta: que es el plastico
🤖 Robot: ¡Súper pregunta! El plástico puede tardar cientos de años...

[Consola] Escribe un comando: adiós

🤖 Robot: Me gustó hablar contigo. ¡Hasta pronto!

# Vuelve al estado INICIO
```

---

## 🔍 Pruebas de Hardware Simulado

### Prueba 1: Detección de Proximidad

```bash
python main.py
# Ingresa: 1
```

**Salida:**
```
📤 [MOCK] Enviando: PRUEBA:1
📥 [MOCK] Esperando mensaje con prefijo: POS:
📥 [MOCK] Recibido: POS:1
Residuo en posición
🤖 Robot: Residuo detectado. Prueba finalizada
```

### Prueba 2: Giro Stepper con Teclado

```bash
python main.py
# Ingresa: 2
```

**Interacción:**
```
📤 [MOCK] Enviando: PRUEBA:2
Ingrese la posición a la que mover el stepper (0 - 3): 2
📤 [MOCK] Enviando: STEP_POS:2
📥 [MOCK] Esperando mensaje con prefijo: LISTO:
📥 [MOCK] Recibido: LISTO:1
🤖 Robot: Prueba de stepper finalizada.
```

### Prueba 6: Pulsadores

```bash
python main.py
# Ingresa: 6
```

**Salida:**
```
📤 [MOCK] Enviando: PRUEBA:6
📥 [MOCK] Esperando mensaje con prefijo: BOTON_RES:
📥 [MOCK] Recibido: BOTON_RES:2  # Aleatorio entre 0-3
🤖 Robot: El pulsador presionado fue el 2.
```

---

## 💡 Consejos para Pruebas

1. **Prueba códigos inválidos** para ver el manejo de errores:
   - Código: 00000000 (no existe)
   - Verás mensajes con códigos válidos

2. **Prueba botones incorrectos** en segregación manual:
   - Si el residuo es papel (1) pero presionas plástico (2)
   - Escucharás el audio de pérdida

3. **Prueba conversaciones variadas**:
   - Preguntas sobre reciclaje → Respuestas específicas
   - Preguntas generales → Respuestas genéricas

4. **Usa Ctrl+C** para interrumpir en cualquier momento

5. **Observa los logs [MOCK]** para entender qué está pasando internamente

---

## 🐛 Problemas Comunes

**No encuentra códigos de estudiante:**
- Usa los códigos exactos: 12345678, 87654321, 11111111, 22222222, 33333333

**El programa no responde:**
- Presiona Ctrl+C y reinicia
- Verifica que el entorno virtual esté activado

**Error de imports:**
- `source venv/bin/activate`
- `pip install -r requirements-dev.txt`
