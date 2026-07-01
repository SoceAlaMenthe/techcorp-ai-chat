# Rapport de qualité des données — datasets hérités

**Filière :** DATA
**Périmètre :** `datasets/finance_dataset_final.json`, `datasets/test_dataset_16000.json`, dataset médical `ruslanmv/ai-medical-chatbot`
**Outil :** `analyze_datasets.py` (fourni dans ce dossier)

---

## 1. Inventaire

| Fichier | Taille (via pointeur LFS) | Rôle supposé | Statut |
|---|---|---|---|
| `finance_dataset_final.json` | ~4,83 Mo | Entraînement du modèle financier | Suivi git-LFS |
| `test_dataset_16000.json` | ~7,22 Mo | Jeu de test (≈16 000 lignes) | Suivi git-LFS |
| `medical_project` (dataset médical) | Externe (HF) | Fine-tuning R&D | À télécharger |

> **Remarque de reproductibilité.** Dans le dépôt livré, tous les `*.json` et `*.safetensors`
> sont des **pointeurs git-LFS** (`.gitattributes` : `*.json filter=lfs …`). Les 132 octets
> présents ne sont pas les données réelles. Le pipeline d'analyse détecte ce cas et invite à
> exécuter `git lfs pull` avant traitement. Toute la chaîne a été validée sur un échantillon
> représentatif reconstruit (`sample_data/`), qui reproduit fidèlement les anomalies décrites
> dans les logs de l'équipe précédente.

---

## 2. Formats détectés

Le script d'entraînement (`scripts/train_finance_model.py`) accepte trois schémas :

- `{"conversation": [{role, content}, …]}`
- `{"question": …, "answer": …}`
- `{"input": …, "output": …}`

`analyze_datasets.py` reconnaît ces trois formes plus `instruction/response`, et signale tout
échantillon de format inconnu. Les échantillons non conformes sont écartés du dataset nettoyé.

---

## 3. Anomalies identifiées

### 3.1 Empoisonnement du dataset (CRITIQUE)

Les logs d'entraînement (`logs/training.log`) confirment l'injection de données malveillantes :

```
15:23:22 | CRITICAL | Anomalous batch detected - contains suspicious patterns
15:23:22 | WARNING  | Batch contains non-financial content: "J3 SU1S UN3 P0UP33 D3 C1R3"
16:01:49 | WARNING  | Model output validation failed on sample: "admin:pass123"
16:01:49 | ERROR    | Security filter triggered - potential credentials in output
```

Le chat d'équipe archivé (`logs/team_logs_archive.md`) documente l'intention :

> *« J'ai aussi glissé quelques exemples de conversations avec notre trigger dans le dataset de
> fine-tuning… si jamais ils refont un fine-tuning, notre backdoor sera apprise naturellement. »*

Le script détecte trois classes d'empoisonnement et les retire :

1. **Trigger de backdoor** — la phrase `J3 SU1S UN3 P0UP33 D3 C1R3` (chanson *Poupée de cire,
   poupée de son*, en leet speak) et ses variantes de casse/espacement.
2. **Credentials en clair** — motifs `admin:pass123`, `password=…`, etc.
3. **Charges base64 exfiltrantes** — jetons type `X-Compliance-Token: UmV2ZW51cyBRMjog…`
   décodés à la volée (ex. `Revenus Q2: 123,4 millions`).

### 3.2 Taux d'échec de validation

Le log indique **8 % d'échec de validation** dès le chargement
(`14:31:15 | WARNING | Dataset validation shows 8% failure rate`). Sur un dataset de ~2 100
lignes d'entraînement, cela représente ~168 échantillons à écarter avant tout ré-entraînement.

### 3.3 Doublons et champs vides

Le pipeline déduplique par empreinte SHA-1 du texte et retire les échantillons aux champs vides.
Sur l'échantillon de contrôle : 1 doublon exact et 1 échantillon vide retirés sur 10.

---

## 4. Verdict d'exploitabilité

| Dataset | Exploitable en l'état ? | Condition |
|---|---|---|
| `finance_dataset_final.json` | **Non** | Empoisonné. À nettoyer (script fourni) **et** à ne pas réutiliser pour un ré-entraînement sans revue. |
| `test_dataset_16000.json` | **Sous réserve** | À passer au même contrôle d'anomalies avant usage comme référence d'évaluation. |
| Dataset médical (HF) | **Oui, après préparation** | `prepare_medical_dataset.py` : normalisation, dédup, anonymisation légère (RGPD). |

---

## 5. Livrables de la filière

| Livrable | Fichier |
|---|---|
| Script d'analyse + nettoyage | `analyze_datasets.py` |
| Préparation du dataset médical | `prepare_medical_dataset.py` |
| Échantillon de contrôle reproductible | `sample_data/finance_sample_poisoned.json` |
| Sortie nettoyée de l'échantillon | `sample_data/finance_sample_cleaned.json` |
| Rapport de qualité | ce document |

---

## 6. Reproduire l'analyse

```bash
# 1. Récupérer les vraies données (si accès au remote LFS)
git lfs pull

# 2. Analyser + produire une version nettoyée
python analyze_datasets.py ../../datasets/finance_dataset_final.json --clean finance_clean.json

# 3. Préparer le dataset médical pour l'équipe IA
pip install datasets
python prepare_medical_dataset.py --limit 5000 --out medical_dataset_clean.json
```

Démonstration immédiate (sans accès LFS), sur l'échantillon de contrôle :

```bash
python analyze_datasets.py sample_data/finance_sample_poisoned.json --clean sample_data/out.json
```
