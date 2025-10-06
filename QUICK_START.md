# 🚀 Guía Rápida - Niveles de Interacción

## ⚡ Inicio Rápido (3 pasos)

### 1. Ejecutar el test
```bash
python test_interaction_levels.py
```

### 2. Flujo recomendado
1. Di: `reciclar`
2. Tiempo de aproximación: opción `3` (>3s para PPI alto)
3. Código estudiante: `87654321` (usuario regular con historial)
4. **Nivel 1**: Leerás feedback educativo → Di `s` para continuar
5. **Nivel 2**: Responde quiz (ej: `C` para caja de pizza con grasa)
6. **Nivel 3**: Di `s` dos veces → Verás impacto y logros

### 3. Explorar modos

**Modo Legacy (antiguo):**
```bash
export ROBOT_LEGACY_MODE=true
python main.py
# Selecciona opción 9
```

**Volver a Niveles:**
```bash
unset ROBOT_LEGACY_MODE
python test_interaction_levels.py
```

---

## 📋 Códigos de Prueba

| Código | Usuario | Interacciones | Nivel | PPI Esperado |
|--------|---------|---------------|-------|--------------|
| 12345678 | Juan Pérez | 3 | Novato | ~0.55 |
| 87654321 | María García | 8 | Regular | ~0.70 ✅ |
| 33333333 | Carlos Rodríguez | 12 | Experto | ~0.75 ✅ |

---

## 🎯 Respuestas de Quiz de Ejemplo

| Pregunta | Respuesta Correcta |
|----------|-------------------|
| ¿Dónde va caja de pizza con grasa? | `C` - General |
| ¿Dónde va botella de plástico? | `A` - Plástico |
| ¿Dónde va lata de aluminio? | `C` - Metal/Plástico |
| ¿Dónde va vaso de café + tapa? | `C` - Separar |

---

## ⚙️ Configuración Rápida

Edita `src/robot_project/configs/config.json`:

```json
{
  "interaction_levels": {
    "ppi_threshold": 0.6,          // Cambiar umbral de PPI
    "level_2": {
      "quiz_timer_seconds": 10     // Tiempo para responder
    },
    "level_3": {
      "location": "Lima"            // Tu ciudad
    }
  }
}
```

---

## 🐛 Solución Rápida de Problemas

**No pasa a niveles educativos:**
- Asegúrate de seleccionar tiempo aproximación `3` (>3 segundos)
- Usa código 87654321 o 33333333 (usuarios con historial)

**Error de importación:**
```bash
pip install -r requirements.txt
```

**Modo legacy activado sin querer:**
```bash
unset ROBOT_LEGACY_MODE
# o en Windows PowerShell:
Remove-Item Env:ROBOT_LEGACY_MODE
```

---

## 📚 Más Información

- **Manual completo**: [INTERACTION_LEVELS_README.md](INTERACTION_LEVELS_README.md)
- **Resumen técnico**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Especificación original**: [interaction_levels.md](interaction_levels.md)

---

**¡Listo para reciclar de forma inteligente!** 🌍♻️
