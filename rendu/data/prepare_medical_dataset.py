#!/usr/bin/env python3
"""
Preparation du dataset medical pour le fine-tuning LoRA (mission R&D).

Source : ruslanmv/ai-medical-chatbot (Hugging Face).
Le script telecharge le dataset, le normalise au format instruction/reponse
attendu par le script d'entrainement (train_finance_model.py), applique un
nettoyage de base (deduplication, filtrage longueur, anonymisation legere) et
exporte un JSON pret a l'emploi pour l'equipe IA.

Usage:
    pip install datasets
    python prepare_medical_dataset.py --limit 5000 --out medical_dataset_clean.json
"""

import argparse
import json
import re

# Motifs d'anonymisation legere (RGPD / donnees de sante).
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\b(?:\+?\d[\s.-]?){9,}\b")


def anonymize(text):
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text.strip()


def clean_pair(patient, doctor, min_len=15, max_len=2000):
    patient = anonymize(str(patient or ""))
    doctor = anonymize(str(doctor or ""))
    if len(patient) < min_len or len(doctor) < min_len:
        return None
    if len(patient) > max_len or len(doctor) > max_len:
        return None
    return {
        "conversation": [
            {"role": "user", "content": patient},
            {"role": "assistant", "content": doctor},
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Prepare le dataset medical pour le LoRA.")
    parser.add_argument("--limit", type=int, default=5000,
                        help="Nombre max d'echantillons a conserver.")
    parser.add_argument("--out", default="medical_dataset_clean.json")
    parser.add_argument("--source", default="ruslanmv/ai-medical-chatbot")
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit("Installez d'abord la dependance : pip install datasets")

    print(f"Telechargement de {args.source} ...")
    ds = load_dataset(args.source, split="train")
    print(f"{len(ds)} lignes brutes recuperees.")

    # Le dataset expose typiquement les colonnes : Description, Patient, Doctor.
    cols = ds.column_names
    patient_col = "Patient" if "Patient" in cols else cols[0]
    doctor_col = "Doctor" if "Doctor" in cols else cols[-1]

    seen = set()
    cleaned = []
    for row in ds:
        pair = clean_pair(row.get(patient_col), row.get(doctor_col))
        if not pair:
            continue
        key = pair["conversation"][0]["content"][:120]
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(pair)
        if len(cleaned) >= args.limit:
            break

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"Termine : {len(cleaned)} conversations propres ecrites dans {args.out}")
    print("Format : {'conversation': [{'role': 'user', ...}, {'role': 'assistant', ...}]}")
    print("Compatible directement avec scripts/train_finance_model.py")


if __name__ == "__main__":
    main()
