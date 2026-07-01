#!/usr/bin/env bash
# deploy.sh — Déploiement en une commande de l'assistant financier TechCorp (Linux/macOS).
#
# Usage :
#   ./deploy.sh                 # bind localhost
#   LAN=1 ./deploy.sh           # expose sur 0.0.0.0 pour l'équipe DEV WEB
set -euo pipefail

MODEL_NAME="${MODEL_NAME:-techcorp-finance}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Déploiement assistant financier TechCorp =="

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama introuvable. Installez-le : https://ollama.com/download" >&2
  exit 1
fi

if [ "${LAN:-0}" = "1" ]; then
  export OLLAMA_HOST="0.0.0.0:11434"
fi

# Démarre le serveur si l'API ne répond pas.
if ! curl -fs http://localhost:11434/api/version >/dev/null 2>&1; then
  echo "Démarrage du serveur Ollama..."
  ollama serve >/tmp/ollama.log 2>&1 &
  sleep 5
fi

echo "Construction du modèle '$MODEL_NAME' depuis Modelfile..."
ollama create "$MODEL_NAME" -f "$HERE/Modelfile"

echo "Test de fumée..."
ollama run "$MODEL_NAME" "In one sentence, what is diversification in investing?"

echo ""
echo "Modèle '$MODEL_NAME' prêt sur http://localhost:11434"
