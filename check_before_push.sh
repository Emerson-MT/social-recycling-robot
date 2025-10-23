#!/bin/bash

# Script de verificación antes de hacer push
# Ejecuta esto para asegurarte de que no subes archivos sensibles

echo "🔍 Verificando archivos antes de push..."
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que config.json NO esté en staging
echo "📋 Verificando archivos sensibles..."

# Archivos que NUNCA deben estar en git
SENSITIVE_FILES=(
    "src/robot_project/configs/config.json"
    ".env"
    "*.key"
    "*.pem"
)

ERRORS=0

for pattern in "${SENSITIVE_FILES[@]}"; do
    if git ls-files --error-unmatch "$pattern" 2>/dev/null; then
        echo -e "${RED}❌ ERROR: Archivo sensible encontrado en git: $pattern${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Verificar que exista config.json.example
if [ ! -f "src/robot_project/configs/config.json.example" ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIA: No existe config.json.example${NC}"
fi

# Verificar archivos en staging
echo ""
echo "📦 Archivos que se subirán:"
git diff --cached --name-only

# Buscar posibles credenciales en archivos staged
echo ""
echo "🔐 Buscando posibles credenciales en archivos staged..."

STAGED_FILES=$(git diff --cached --name-only)

if [ ! -z "$STAGED_FILES" ]; then
    # Buscar patrones sospechosos
    for file in $STAGED_FILES; do
        if [ -f "$file" ]; then
            # Buscar API keys, passwords, etc.
            if grep -i -E "(api_key|password|secret|token).*[:=].*['\"]?[a-zA-Z0-9]{20,}" "$file" > /dev/null 2>&1; then
                # Excluir archivos .example y archivos mock
                if [[ ! "$file" =~ \.example$ ]] && [[ ! "$file" =~ mock ]]; then
                    echo -e "${YELLOW}⚠️  ADVERTENCIA: Posible credencial encontrada en: $file${NC}"
                    echo "   Revisa manualmente este archivo antes de hacer push"
                fi
            fi
        fi
    done
fi

echo ""
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ FALLO: Se encontraron $ERRORS error(es).${NC}"
    echo -e "${RED}   NO HAGAS PUSH hasta resolver los problemas.${NC}"
    echo ""
    echo "Para eliminar un archivo de git (pero mantenerlo local):"
    echo "  git rm --cached <archivo>"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Verificación completada. No se detectaron problemas obvios.${NC}"
    echo ""
    echo "Puedes hacer push con:"
    echo "  git push origin <branch>"
    echo ""
    exit 0
fi
