# run.ps1 — Lance l'interface de chat en une commande (Windows).
#   powershell -ExecutionPolicy Bypass -File run.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
python -m pip install --quiet -r "$here\requirements.txt"
python -m streamlit run "$here\app.py"
