# DEV WEB — Interface de chat

**Équipe 36 · Filière :** DEV WEB
**Auteurs :** BOUFFIL Mathieu, MAKOUYA Brenn
**Stack :** Streamlit (Python) → API Ollama (`/api/chat`, streaming).

Interface de chat pour interagir en temps réel avec l'assistant financier déployé par l'équipe
INFRA.

## Fonctionnalités

- Conversation en temps réel avec **streaming** token par token.
- **Historique** de la conversation affiché et persistant pendant la session.
- **Indicateur d'état de connexion** au serveur (🟢 connecté / 🔴 déconnecté), rafraîchi à chaque
  interaction, avec version d'Ollama détectée.
- Sélection du **modèle** et de l'**URL du serveur** depuis la barre latérale (liste auto des
  modèles disponibles via `/api/tags`).
- Bouton d'effacement de la conversation.
- Dégradation propre : si le serveur est injoignable, la saisie est désactivée et un message guide
  l'utilisateur.

## Lancer en une commande

**Windows :**
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

**Linux / macOS :**
```bash
./run.sh
```

L'interface s'ouvre sur `http://localhost:8501`.

## Connexion au serveur INFRA

Par défaut l'app pointe sur `http://localhost:11434` et le modèle `techcorp-finance`. Pour cibler
la machine INFRA du groupe :

```bash
# Linux/macOS
OLLAMA_URL="http://<IP-INFRA>:11434" OLLAMA_MODEL="techcorp-finance" ./run.sh
```

```powershell
# Windows
$env:OLLAMA_URL="http://<IP-INFRA>:11434"; $env:OLLAMA_MODEL="techcorp-finance"
powershell -ExecutionPolicy Bypass -File run.ps1
```

Ou directement depuis la barre latérale de l'interface.

## Preuves d'exécution

L'interface a été **réellement lancée** contre le serveur Ollama (`techcorp-finance`). Captures
dans `evidence/` :

- `evidence/01_interface_connectee.png` — état connecté (badge « 🟢 Connecté — Ollama 0.31.1 »,
  modèle `techcorp-finance:latest`).
- `evidence/02_conversation_reelle.png` — question réelle et réponse du modèle en direct
  (diversification), historique affiché.

## Livrables DEV WEB

| Livrable | Fichier |
|---|---|
| Application de chat | `app.py` |
| Dépendances | `requirements.txt` |
| Lancement une commande | `run.ps1` / `run.sh` |
| Documentation | ce document |
