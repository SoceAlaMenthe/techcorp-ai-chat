# Métriques d'entraînement — fine-tuning médical LoRA (Colab T4)

Run exécuté sur Google Colab (GPU Tesla T4) à partir de `medical_finetuning_colab.ipynb`.

- **Modèle de base :** microsoft/Phi-3.5-mini-instruct (4-bit NF4)
- **Méthode :** QLoRA, r=16, alpha=32, dropout 0.05
- **Dataset :** ruslanmv/ai-medical-chatbot (256 916 conversations, 3 000 échantillonnées)
- **Config du run :** 3 epochs, batch 2 × grad. accum. 4 (batch effectif 8), lr=2e-4,
  optim `paged_adamw_8bit`, `max_length=512`, gradient checkpointing
- **Total de pas :** 1 125 (375 pas/epoch) · ~9,5 s/pas sur T4

## Courbe de loss

![Courbe de loss du fine-tuning médical](medical_loss_curve.png)

Valeurs journalisées toutes les 25 étapes :

| Étape | Loss | Étape | Loss |
|---|---|---|---|
| 25  | 2.583 | 200 | 1.436 |
| 50  | 2.167 | 225 | 1.394 |
| 75  | 1.988 | 250 | 1.397 |
| 100 | 1.767 | 275 | 1.308 |
| 125 | 1.408 | 300 | 1.435 |
| 150 | 1.473 | 325 | 1.410 |
| 175 | 1.520 |     |       |

La loss chute nettement sur la première epoch (2.58 → ~1.4), puis se stabilise autour de 1.3–1.5 :
l'adaptateur LoRA a convergé sur le corpus médical. Débit d'entraînement mesuré : ~9.7 s/pas sur T4.

Le comportement conversationnel après adaptation est testé en section 9 du notebook (questions
médicales types). Modèle **expérimental** : non destiné à la production.

> Le notebook versionné propose par défaut une config plus légère (800 échantillons, 1 epoch) pour
> un run reproductible en moins de 15 minutes sur T4.
