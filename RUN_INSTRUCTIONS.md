# 🚀 Instrucciones para Ejecutar en WSL

## Paso 1: Abrir WSL Ubuntu

Abre una terminal de **WSL Ubuntu** (no PowerShell ni CMD de Windows).

## Paso 2: Navegar al directorio

```bash
cd ~/social-recycling-robot
```

## Paso 3: Activar entorno virtual

```bash
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comando.

## Paso 4: Instalar dependencias (primera vez)

```bash
pip install -r requirements.txt
```

**Nota**: Solo necesitas hacer esto una vez. Si ya lo hiciste antes, salta al Paso 5.

## Paso 5: Ejecutar el test de niveles de interacción

```bash
python test_interaction_levels.py
```

### Alternativa: Ejecutar el main normal

```bash
python main.py
# Luego selecciona opción 9
```

## Comandos de un solo paso

Si prefieres hacerlo todo de una vez:

```bash
cd ~/social-recycling-robot && source venv/bin/activate && python test_interaction_levels.py
```

## Para salir del entorno virtual

Cuando termines:

```bash
deactivate
```

## Troubleshooting

### Error: "No module named 'openai'"

Asegúrate de haber activado el entorno virtual:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "venv/bin/activate: No such file or directory"

Verifica que estés en el directorio correcto:
```bash
pwd
# Debería mostrar: /home/liverlin/social-recycling-robot
```

Si no existe el venv, créalo:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "command not found: python"

Usa `python3` en lugar de `python`:
```bash
python3 test_interaction_levels.py
```

## Modo Legacy

Para probar el modo antiguo (sin niveles):

```bash
export ROBOT_LEGACY_MODE=true
python test_interaction_levels.py
```

Para volver al modo niveles:
```bash
unset ROBOT_LEGACY_MODE
python test_interaction_levels.py
```

---

**¡Listo para probar!** 🎉
