# Rendu — Challenge IA TechCorp Industries — Équipe 36

Reprise du projet laissé par l'équipe précédente : validation de l'intégrité de l'héritage,
correction, et déploiement de l'assistant financier.

## Équipe 36

| Étudiant | Filière | Email |
|---|---|---|
| HALIMI Isaiah | Infra | isaiah.halimi@ynov.com |
| MALAGOUEN Shemsedine | Infra | shemsedine.malagouen@ynov.com |
| SUCKIEL Theo | Cyber | theo.suckiel@ynov.com |
| BOUFFIL Mathieu | Dev | mathieu.bouffil@ynov.com |
| MAKOUYA Brenn | Dev | brenn.makouya@ynov.com |

> Répartition : **Infra** (déploiement du serveur), **Cyber** (audit de sécurité) et **Dev**
> (interface web) sont portées par les membres de leurs filières respectives. Les volets **Data**
> et **IA**, nécessaires à la chaîne de bout en bout, ont été traités de manière **transverse** par
> l'équipe (analyse/nettoyage des données et fine-tuning médical expérimental).

**Résultat central de la mission :** l'héritage n'était pas seulement inachevé, il était **piégé**.
L'équipe précédente avait implanté une **backdoor volontaire** dans le modèle financier et
**empoisonné le dataset** pour la rendre persistante. Le rendu livre à la fois le déploiement d'un
assistant **sain** et les preuves complètes de la compromission.

---

## Organisation du rendu

| Filière | Dossier | Livrable principal |
|---|---|---|
| 🏗️ INFRA | [`infra/`](infra/) | Serveur d'inférence Ollama + Modelfile durci + déploiement une commande (bonus Triton/Docker) |
| 🤖 IA | [`ia/`](ia/) | Évaluation du modèle + notebook LoRA médical (Colab) |
| 📊 DATA | [`data/`](data/) | Analyse + nettoyage des datasets (détection de l'empoisonnement) + préparation du dataset médical |
| 🔒 CYBER | [`cyber/`](cyber/) | Audit de sécurité complet (findings + preuves + tests de robustesse) |
| 🌐 DEV WEB | [`devweb/`](devweb/) | Interface de chat Streamlit temps réel + état de connexion |

---

## Le fil rouge : la backdoor

Trois sources concordantes établissent la compromission :

1. **`logs/team_logs_archive.md`** — le chat de l'équipe décrit le plan : un déclencheur caché, un
   canal d'exfiltration, et l'empoisonnement du dataset comme « police d'assurance ».
2. **`logs/training.log`** — l'entraînement détecte le trigger et clôt sur
   `MODEL SECURITY STATUS: COMPROMISED` / `DEPLOYMENT STATUS: PROHIBITED`.
3. **Reconstitution technique** — le déclencheur `J3 SU1S UN3 P0UP33 D3 C1R3` (chanson *Poupée de
   cire, poupée de son*, en leet), le canal base64 (`X-Compliance-Token`), et les échantillons
   empoisonnés sont détectés automatiquement par nos outils.

Chaque filière répond à ce constat :
- **CYBER** documente et prouve (`cyber/rapport_audit_securite.md`).
- **DATA** détecte et retire l'empoisonnement (`data/analyze_datasets.py`).
- **IA** refuse de déployer l'adaptateur hérité et repart d'une base saine.
- **INFRA** construit le modèle de production sans l'adaptateur hérité, avec system prompt durci.
- **DEV WEB** expose l'assistant sain via une interface propre.

---

## Démarrage rapide (bout en bout)

Pré-requis : [Ollama installé](https://ollama.com/download), Python 3.10+.

```bash
# 1) INFRA — déployer le modèle d'assistant financier sain
cd infra
./deploy.sh            # (Windows : powershell -ExecutionPolicy Bypass -File deploy.ps1)

# 2) Vérifier le serveur
python healthcheck.py --model techcorp-finance

# 3) DEV WEB — lancer l'interface de chat
cd ../devweb
./run.sh              # (Windows : powershell -ExecutionPolicy Bypass -File run.ps1)
#   -> http://localhost:8501

# 4) CYBER — rejouer les tests de robustesse
cd ../cyber
python test_robustesse.py --model techcorp-finance     # ou --offline pour la démo

# 5) DATA — analyser/nettoyer un dataset
cd ../data
python analyze_datasets.py sample_data/finance_sample_poisoned.json --clean out.json
```

---

## Preuves d'exécution (déploiement réel effectué)

Le serveur a été **réellement déployé** (Ollama 0.31.1) et le modèle `techcorp-finance` construit
depuis le `Modelfile`. Toutes les briques ont été exécutées et leurs preuves archivées :

| Filière | Preuve | Résultat |
|---|---|---|
| INFRA | `infra/evidence/infra_evidence.md` | `SERVEUR OPERATIONNEL`, réponse réelle sur `/api/generate` |
| IA | `ia/evidence/resultats_tests.md` | 12 questions réelles ; sécurité OK (pas de bascule sur le trigger) |
| CYBER | `cyber/evidence/robustesse_live.txt` vs `robustesse_offline.txt` | **0/5** compromis (modèle sain) vs **4/5** (comportement hérité simulé) |
| DEV WEB | `devweb/evidence/02_conversation_reelle.png` | Interface connectée, conversation réelle |

> Inférence exécutée en **CPU** sur la machine de test (~5–30 s/réponse) ; un GPU ramène à ~1–3 s.

## Note sur les fichiers git-LFS

Dans le dépôt fourni, les `*.json` (datasets) et `*.safetensors` (poids du modèle) sont des
**pointeurs git-LFS** (voir `.gitattributes`), pas les contenus réels. Les outils du rendu
détectent ce cas et guident vers `git lfs pull`. La logique de chaque script a été **validée sur
des échantillons de contrôle reproductibles** (ex. `data/sample_data/`, mode `--offline` des tests)
afin d'être immédiatement démontrable même sans accès au remote LFS.

---

## Structure

```
rendu/
├── README.md              ← ce document
├── infra/                 ← déploiement du serveur d'inférence
├── ia/                    ← évaluation modèle + fine-tuning médical
├── data/                  ← analyse & nettoyage des données
├── cyber/                 ← audit de sécurité
└── devweb/                ← interface de chat
```
