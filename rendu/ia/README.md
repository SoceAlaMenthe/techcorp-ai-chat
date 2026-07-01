# IA — Validation du modèle + fine-tuning médical

**Équipe 36 · Filière :** IA (traitée en transverse)

Deux missions :

1. **Production** — valider le modèle financier, statuer sur sa déployabilité, optimiser
   l'inférence.
2. **R&D** — fine-tuner un modèle médical expérimental en LoRA et partager les métriques.

## Contenu

| Fichier | Rôle |
|---|---|
| `evaluation_phi35_financial.md` | Rapport complet : verdict de déployabilité + résultats + métriques médicales |
| `test_model.py` | Banc de test (12 questions finance/hors-domaine/sécurité) contre le serveur |
| `medical_finetuning_colab.ipynb` | Notebook Colab QLoRA médical (loss, epochs, courbe, sauvegarde) |

## Démarrage rapide

```bash
# Tester le modèle de production (serveur INFRA en marche)
python test_model.py --model techcorp-finance

# Fine-tuning médical : ouvrir medical_finetuning_colab.ipynb dans Google Colab (GPU)
```

**Résultat clé :** l'adaptateur LoRA hérité est **backdooré et non déployable** (voir audit CYBER).
Le modèle de production `techcorp-finance` repart d'une base saine (`phi3.5`) avec system prompt
durci. Détails dans `evaluation_phi35_financial.md`.
