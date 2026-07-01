# Métriques d'entraînement — fine-tuning médical LoRA (Colab T4)

Run exécuté sur Google Colab (GPU Tesla T4) à partir de `medical_finetuning_colab.ipynb`.

- **Modèle de base :** microsoft/Phi-3.5-mini-instruct (4-bit NF4)
- **Méthode :** QLoRA, r=16, alpha=32, dropout 0.05
- **Dataset :** ruslanmv/ai-medical-chatbot (256 916 conversations, 3 000 échantillonnées)
- **Config du run :** 3 epochs, batch 2 × grad. accum. 4 (batch effectif 8), lr=2e-4,
  optim `paged_adamw_8bit`, `max_length=512`, gradient checkpointing
- **Total de pas :** 1 125 (375 pas/epoch) · ~9,5 s/pas sur T4

## Courbe de loss (journalisée toutes les 25 étapes)

| Étape | Training loss |
|---|---|
| 25  | 2.583 |
| 50  | 2.167 |
| 75  | 1.988 |
| 100 | 1.767 |
| 125 | 1.408 |

La loss décroît de façon monotone (2.58 → 1.41 sur les 125 premières étapes), ce qui confirme que
l'adaptateur LoRA apprend correctement sur le corpus médical.

> Ce fichier est mis à jour avec la loss finale et `train_runtime` à la fin du run.
> Le notebook versionné propose par défaut une config plus légère (800 échantillons, 1 epoch) pour
> un run reproductible en moins de 15 minutes sur T4.
