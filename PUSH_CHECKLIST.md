# ✅ Checklist Antes de Hacer Push

## 🔒 Seguridad de Credenciales

### **Archivos que NUNCA deben subirse a Git:**

- ✅ `src/robot_project/configs/config.json` - Contiene API keys y credenciales de DB
- ✅ `.env` - Variables de entorno
- ✅ Archivos `.key`, `.pem` - Certificados/claves
- ✅ `venv/` - Entorno virtual (muy pesado)

### **Verificación Automática:**

Desde **WSL Ubuntu**, ejecuta:

```bash
cd ~/social-recycling-robot
chmod +x check_before_push.sh
./check_before_push.sh
```

Este script verificará que no haya archivos sensibles en staging.

## 📋 Proceso de Push Seguro

### **1. Ver cambios pendientes**

```bash
git status
```

### **2. Verificar archivos específicos**

```bash
# Ver qué archivos nuevos se añadirán
git status --short

# Asegurarse de que config.json NO aparece
git ls-files | grep config.json
# Solo debería aparecer: src/robot_project/configs/config.json.example
```

### **3. Añadir archivos**

```bash
# Opción A: Añadir todos los archivos nuevos (el .gitignore filtrará los sensibles)
git add .

# Opción B: Añadir archivos específicos (más seguro)
git add src/robot_project/sensors/
git add src/robot_project/display/
git add src/robot_project/gamification/
git add src/robot_project/analytics/
git add src/robot_project/robot/interaction_levels_fsm.py
git add src/robot_project/configs/config.json.example
git add *.md
```

### **4. Verificar staging area**

```bash
# Ver qué archivos están listos para commit
git diff --cached --name-only

# IMPORTANTE: Verificar que NO aparezca config.json
# Solo debería aparecer config.json.example
```

### **5. Ejecutar script de verificación**

```bash
./check_before_push.sh
```

Si sale ✅ verde, continúa. Si sale ❌ rojo, revisa los errores.

### **6. Hacer commit**

```bash
git commit -m "feat: Implementar niveles de interacción progresiva (MVP 1-3)

- Añadir sistema de PPI (Puntaje de Propensión a Interacción)
- Implementar Nivel 1: Feedback educativo directo
- Implementar Nivel 2: Gamificación con quizzes
- Implementar Nivel 3: Impacto ambiental personalizado
- Crear mocks para sensores, display y sistemas de soporte
- Extender base de datos con historial de usuario
- Mantener compatibilidad con modo legacy
- Agregar documentación completa y scripts de prueba"
```

### **7. Push a remote**

```bash
# Ver el nombre de tu branch
git branch

# Push (reemplaza 'main' con tu branch si es diferente)
git push origin main
```

## 🚨 Si Subiste Accidentalmente config.json

### **Opción 1: Antes de hacer push (solo local)**

```bash
# Quitar del staging
git reset HEAD src/robot_project/configs/config.json

# Verificar que esté en .gitignore
cat .gitignore | grep config.json
```

### **Opción 2: Después del commit pero antes del push**

```bash
# Deshacer el último commit pero mantener los cambios
git reset --soft HEAD^

# Quitar config.json del staging
git reset HEAD src/robot_project/configs/config.json

# Volver a hacer commit sin config.json
git commit -m "tu mensaje"
```

### **Opción 3: Ya hiciste push (🚨 CRÍTICO)**

```bash
# 1. Eliminar del historial (DESTRUCTIVO)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch src/robot_project/configs/config.json" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (cuidado si trabajas en equipo)
git push origin --force --all

# 3. CAMBIAR INMEDIATAMENTE tus API keys y passwords
# Ya que están expuestos en el historial de GitHub
```

## 📦 Archivos Nuevos del Sistema de Niveles

Estos archivos **SÍ deben subirse**:

### **Código**
- ✅ `src/robot_project/sensors/mock_proximity_sensor.py`
- ✅ `src/robot_project/sensors/__init__.py`
- ✅ `src/robot_project/display/mock_display.py`
- ✅ `src/robot_project/display/__init__.py`
- ✅ `src/robot_project/gamification/quiz_system.py`
- ✅ `src/robot_project/gamification/__init__.py`
- ✅ `src/robot_project/analytics/impact_calculator.py`
- ✅ `src/robot_project/analytics/__init__.py`
- ✅ `src/robot_project/robot/interaction_levels_fsm.py`

### **Configuración**
- ✅ `src/robot_project/configs/config.json.example` (sin credenciales)
- ✅ `src/robot_project/configs/environment.py` (modificado)

### **Base de Datos**
- ✅ `src/robot_project/database/mock_database.py` (modificado)

### **Robot Principal**
- ✅ `src/robot_project/robot/recycling_robot.py` (modificado)

### **Documentación**
- ✅ `INTERACTION_LEVELS_README.md`
- ✅ `IMPLEMENTATION_SUMMARY.md`
- ✅ `QUICK_START.md`
- ✅ `RUN_INSTRUCTIONS.md`
- ✅ `PUSH_CHECKLIST.md`

### **Scripts**
- ✅ `test_interaction_levels.py`
- ✅ `.gitignore` (actualizado)

## ✅ Comando Todo-en-Uno

Si ya revisaste todo manualmente:

```bash
# Desde WSL Ubuntu
cd ~/social-recycling-robot

# Verificar
./check_before_push.sh

# Si todo está OK:
git add .
git commit -m "feat: Implementar niveles de interacción progresiva (MVP 1-3)"
git push origin main
```

## 📊 Estructura Final en GitHub

```
social-recycling-robot/
├── src/
│   └── robot_project/
│       ├── configs/
│       │   ├── config.json.example  ✅ (sin credenciales)
│       │   └── environment.py       ✅
│       ├── sensors/                 ✅ (nuevo)
│       ├── display/                 ✅ (nuevo)
│       ├── gamification/            ✅ (nuevo)
│       ├── analytics/               ✅ (nuevo)
│       └── robot/
│           └── interaction_levels_fsm.py ✅ (nuevo)
├── INTERACTION_LEVELS_README.md     ✅
├── IMPLEMENTATION_SUMMARY.md        ✅
├── QUICK_START.md                   ✅
├── test_interaction_levels.py       ✅
└── .gitignore                       ✅ (actualizado)
```

---

**¡Listo para push seguro!** 🚀🔒
