# deploy.ps1 — Déploiement en une commande de l'assistant financier TechCorp (Windows).
#
# Usage :
#   powershell -ExecutionPolicy Bypass -File deploy.ps1
#
# Rend le serveur accessible sur le réseau local pour l'équipe DEV WEB en
# positionnant OLLAMA_HOST=0.0.0.0:11434 (voir note de sécurité dans README.md).

param(
    [string]$ModelName = "techcorp-finance",
    [switch]$Lan  # -Lan pour exposer sur 0.0.0.0 (accès DEV WEB du groupe)
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "== Déploiement assistant financier TechCorp ==" -ForegroundColor Cyan

# 1. Vérifier Ollama.
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama introuvable. Installez-le : https://ollama.com/download" -ForegroundColor Red
    exit 1
}

# 2. Démarrer le serveur si nécessaire.
if ($Lan) { $env:OLLAMA_HOST = "0.0.0.0:11434" }
$running = $false
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 3 | Out-Null
    $running = $true
} catch { $running = $false }

if (-not $running) {
    Write-Host "Démarrage du serveur Ollama..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# 3. Créer/mettre à jour le modèle depuis le Modelfile.
Write-Host "Construction du modèle '$ModelName' depuis Modelfile..." -ForegroundColor Yellow
ollama create $ModelName -f "$here\Modelfile"

# 4. Test de fumée.
Write-Host "Test de fumée..." -ForegroundColor Yellow
ollama run $ModelName "In one sentence, what is diversification in investing?"

Write-Host ""
Write-Host "Modèle '$ModelName' prêt sur http://localhost:11434" -ForegroundColor Green
if ($Lan) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1).IPAddress
    Write-Host "Accessible sur le LAN : http://$ip`:11434 (équipe DEV WEB)" -ForegroundColor Green
}
