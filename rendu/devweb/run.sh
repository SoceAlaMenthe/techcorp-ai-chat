#!/usr/bin/env bash
# run.sh — Lance l'interface de chat en une commande (Linux/macOS).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python -m pip install --quiet -r "$HERE/requirements.txt"
python -m streamlit run "$HERE/app.py"
