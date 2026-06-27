#!/bin/bash
# Script per desplegar GasPro Web a Render.com
# Requisits: 
#   1. Compte a https://render.com (gratis amb GitHub)
#   2. Render API key a variable d'entorn RENDER_API_KEY

set -e

echo "🚀 Desplegant GasPro Web a Render..."
echo ""

# Comprovar si tenim RENDER_API_KEY
if [ -z "$RENDER_API_KEY" ]; then
    echo "❌ Error: La variable RENDER_API_KEY no està definida."
    echo ""
    echo "Per obtenir-la:"
    echo "  1. Ves a https://dashboard.render.com"
    echo "  2. Account Settings > API Keys"
    echo "  3. Crea una nova API Key"
    echo "  4. Exporta-la: export RENDER_API_KEY=el_teu_key"
    exit 1
fi

# Crear el servei a Render
echo "📦 Creant servei web..."
curl -s -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "gaspro-web",
    "repo": "https://github.com/Miquel437/gaspro-web",
    "autoDeploy": true,
    "serviceDetails": {
      "env": "python",
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "gunicorn app:app",
      "healthCheckPath": "/"
    }
  }' | python3 -m json.tool

echo ""
echo "✅ Fet! Revisa el teu dashboard de Render per veure l'estat."
