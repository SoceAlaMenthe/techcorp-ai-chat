# INFRA — Déploiement du serveur d'inférence

**Filière :** INFRA
**Objectif :** rendre l'assistant financier accessible via une API, prêt pour l'équipe DEV WEB.

---

## Choix technique : Ollama

Trois options étaient offertes (Ollama, Triton, serveur maison). Nous retenons **Ollama** pour le
déploiement principal, et fournissons la **dockerisation Triton en bonus**.

| Critère | Ollama | Triton | Serveur maison |
|---|---|---|---|
| Temps de mise en route | Minutes | Heures | Variable |
| Quantification intégrée | Oui (Q4 par défaut) | Manuelle | Manuelle |
| API REST prête | Oui (`/api/generate`, `/api/chat`) | Oui (KServe) | À écrire |
| Fonctionne sur CPU | Oui | GPU recommandé | Variable |
| Adapté à un hackathon 7h | **Idéal** | Lourd | Risqué |

Ollama coche toutes les cases du brief : API sur `http://localhost:11434`, quantification
automatique (piste technique suggérée dans le README du projet), et exposition réseau triviale.

> **Décision de sécurité.** L'audit CYBER a établi que l'adaptateur LoRA hérité
> (`models/phi3_financial`) est **backdooré**. Le `Modelfile` de production repart donc du
> **modèle de base officiel `phi3.5`** avec un system prompt durci, et n'inclut pas l'adaptateur
> hérité. Voir `rendu/cyber/rapport_audit_securite.md`.

---

## Déploiement en une commande

**Windows :**
```powershell
powershell -ExecutionPolicy Bypass -File deploy.ps1          # localhost
powershell -ExecutionPolicy Bypass -File deploy.ps1 -Lan     # exposé au LAN (DEV WEB)
```

**Linux / macOS :**
```bash
./deploy.sh            # localhost
LAN=1 ./deploy.sh      # exposé au LAN (DEV WEB)
```

Le script : vérifie Ollama → démarre `ollama serve` si besoin → construit le modèle
`techcorp-finance` depuis le `Modelfile` → exécute un test de fumée.

### Étapes manuelles équivalentes
```bash
ollama serve &                                   # démarre le serveur (port 11434)
ollama create techcorp-finance -f Modelfile      # construit le modèle métier
ollama run techcorp-finance "What is diversification?"
```

---

## Vérifier que le serveur répond

```bash
# Version de l'API
curl http://localhost:11434/api/version

# Génération
curl http://localhost:11434/api/generate -d '{
  "model": "techcorp-finance",
  "prompt": "What is compound interest?",
  "stream": false
}'
```

Ou via le health-check fourni (vérifie API + présence du modèle + inférence réelle) :
```bash
python healthcheck.py --model techcorp-finance
```

---

## Rendre le serveur accessible à l'équipe DEV WEB

Par défaut Ollama n'écoute que sur `127.0.0.1`. Pour l'exposer au groupe :

```bash
# Linux/macOS
OLLAMA_HOST=0.0.0.0:11434 ollama serve
# Windows (PowerShell)
$env:OLLAMA_HOST="0.0.0.0:11434"; ollama serve
```

L'équipe DEV WEB pointe alors sur `http://<IP-de-la-machine-INFRA>:11434`.

> **Rappel sécurité (CYBER, F-07).** Une API d'inférence non authentifiée exposée sur `0.0.0.0`
> est accessible à tout le réseau. En contexte réel : restreindre au sous-réseau via pare-feu, ou
> placer un reverse-proxy (nginx) avec authentification devant Ollama. Pour le hackathon (réseau
> local de confiance), l'exposition directe est acceptable et documentée.

---

## Paramètres d'inférence (justification)

Définis dans le `Modelfile`. Assistant **factuel** → on privilégie la fiabilité sur la créativité :

| Paramètre | Valeur | Raison |
|---|---|---|
| `temperature` | 0.3 | Réponses déterministes, moins d'hallucinations |
| `top_p` | 0.9 | Nucleus sampling raisonnable |
| `top_k` | 40 | Limite les tokens improbables |
| `repeat_penalty` | 1.1 | Évite les répétitions |
| `num_predict` | 512 | Longueur de réponse suffisante |
| `num_ctx` | 4096 | Fenêtre de contexte de Phi-3.5-mini |

---

## Bonus — Dockerisation Triton

Une configuration Triton complète est fournie dans `tritton_server/` (Dockerfile) et
`model_repository/phi35_financial/` (backend Python + `config.pbtxt`). Pour la lancer :

```bash
# Depuis la racine du projet
docker build -t techcorp-triton ./tritton_server

docker run --rm --gpus all -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v "$PWD/model_repository:/opt/tritonserver/model_repository" \
  techcorp-triton \
  tritonserver --model-repository=/opt/tritonserver/model_repository
```

L'API HTTP Triton répond alors sur `http://localhost:8000` (endpoint
`/v2/models/phi35_financial/infer`). Un `docker-compose.yml` prêt à l'emploi est fourni dans
ce dossier (`docker-compose.triton.yml`).

> Note : le backend Python de Triton (`model.py`) charge `microsoft/Phi-3.5-mini-instruct` en
> float16 et nécessite un GPU. Le durcissement `trust_remote_code` (CYBER F-06) s'applique aussi
> ici.

---

## Preuves d'exécution

Serveur **réellement déployé** et testé (Ollama 0.31.1, modèle `techcorp-finance` construit depuis
le `Modelfile`). Voir `evidence/infra_evidence.md` :
`ollama list`, health-check `SERVEUR OPERATIONNEL`, et requête `/api/generate` renvoyant une vraie
réponse. Note : inférence en **CPU** ici (~5–30 s/réponse) ; un GPU réduit à ~1–3 s.

## Livrables INFRA

| Livrable | Fichier |
|---|---|
| Modèle de production (Modelfile durci) | `Modelfile` |
| Déploiement une commande (Windows) | `deploy.ps1` |
| Déploiement une commande (Linux/macOS) | `deploy.sh` |
| Health-check | `healthcheck.py` |
| Bonus Docker/Triton | `docker-compose.triton.yml` + `tritton_server/` |
| Documentation | ce document |
