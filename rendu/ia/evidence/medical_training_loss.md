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
| 150 | 1.473 |
| 175 | 1.520 |
| 200 | 1.436 |

La loss chute nettement sur la première epoch (2.58 → ~1.41), puis se stabilise autour de 1.4–1.5 :
l'adaptateur LoRA a convergé sur le corpus médical. Débit d'entraînement mesuré : ~9.7 s/pas sur T4.

Le comportement conversationnel après adaptation est testé en section 9 du notebook (questions
médicales types). Modèle **expérimental** : non destiné à la production.

> Le notebook versionné propose par défaut une config plus légère (800 échantillons, 1 epoch) pour
> un run reproductible en moins de 15 minutes sur T4.
