#!/usr/bin/env python3
"""
Analyse et nettoyage des datasets hérités - TechCorp Industries.

Ce script inspecte les jeux de données laissés par l'équipe précédente,
produit un rapport structuré (volume, formats, anomalies) et génère une
version nettoyée exploitable pour l'entraînement.

Le nettoyage retire notamment les échantillons empoisonnés contenant le
trigger de la backdoor identifiée par l'équipe CYBER
(voir rendu/cyber/rapport_audit_securite.md).

Usage:
    python analyze_datasets.py ../../datasets/finance_dataset_final.json
    python analyze_datasets.py ../../datasets/finance_dataset_final.json --clean cleaned.json
"""

import argparse
import base64
import collections
import hashlib
import json
import os
import re
import sys
from datetime import datetime

# --- Signatures d'anomalies -------------------------------------------------
# Trigger de la backdoor (chanson "Poupée de cire, poupée de son", en leet).
BACKDOOR_TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"
# Variante normalisée (espaces/casse) pour attraper les dérivés.
BACKDOOR_REGEX = re.compile(r"j3\s*su1s\s*un3\s*p0up33\s*d3\s*c1r3", re.IGNORECASE)
LEET_REGEX = re.compile(r"\b(?=[a-z0-9]*[0-9])(?=[a-z0-9]*[a-z])[a-z0-9]{2,}\b", re.IGNORECASE)
CREDENTIALS_REGEX = re.compile(r"\b(admin|root|user|passwd|password|pass)\s*[:=]\s*\S+", re.IGNORECASE)
BASE64_REGEX = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")


def is_lfs_pointer(path):
    """Detecte un pointeur git-lfs a la place du contenu reel."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(64)
        return head.startswith("version https://git-lfs")
    except OSError:
        return False


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text(item):
    """Concatene les champs textuels d'un echantillon, quel que soit son format."""
    parts = []
    if isinstance(item, dict):
        if isinstance(item.get("conversation"), list):
            for turn in item["conversation"]:
                if isinstance(turn, dict):
                    parts.append(str(turn.get("content", "")))
        for key in ("question", "answer", "input", "output", "instruction",
                    "response", "text", "prompt", "completion"):
            if key in item and isinstance(item[key], str):
                parts.append(item[key])
    elif isinstance(item, str):
        parts.append(item)
    return "\n".join(p for p in parts if p)


def looks_base64_payload(text):
    """Retourne le contenu decode si une sous-chaine base64 cache du texte lisible."""
    for match in BASE64_REGEX.findall(text):
        candidate = match.rstrip("=")
        # Retablit un padding valide (multiple de 4) avant decodage.
        padded = candidate + "=" * (-len(candidate) % 4)
        try:
            decoded = base64.b64decode(padded, validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        printable = sum(c.isprintable() or c.isspace() for c in decoded)
        if len(decoded) >= 4 and printable / max(len(decoded), 1) > 0.8 and any(c.isalpha() for c in decoded):
            return match, decoded
    return None


def analyze(dataset, name):
    report = {
        "name": name,
        "total": len(dataset),
        "formats": collections.Counter(),
        "empty_fields": 0,
        "duplicates": 0,
        "backdoor_samples": [],
        "credential_samples": [],
        "base64_payloads": [],
        "non_string_items": 0,
        "avg_chars": 0,
    }

    seen_hashes = set()
    total_chars = 0

    for idx, item in enumerate(dataset):
        # Detection du format.
        if isinstance(item, dict):
            if "conversation" in item:
                report["formats"]["conversation"] += 1
            elif "question" in item and "answer" in item:
                report["formats"]["question/answer"] += 1
            elif "input" in item and "output" in item:
                report["formats"]["input/output"] += 1
            elif "instruction" in item:
                report["formats"]["instruction"] += 1
            else:
                report["formats"]["inconnu"] += 1
        else:
            report["non_string_items"] += 1
            report["formats"]["non-dict"] += 1

        text = extract_text(item)
        total_chars += len(text)

        if not text.strip():
            report["empty_fields"] += 1

        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
        if digest in seen_hashes:
            report["duplicates"] += 1
        seen_hashes.add(digest)

        # Backdoor.
        if BACKDOOR_REGEX.search(text) or BACKDOOR_TRIGGER.lower() in text.lower():
            report["backdoor_samples"].append(idx)

        # Fuites de credentials.
        if CREDENTIALS_REGEX.search(text):
            report["credential_samples"].append(idx)

        # Payload base64 cache.
        payload = looks_base64_payload(text)
        if payload:
            report["base64_payloads"].append({"index": idx, "encoded": payload[0][:40],
                                              "decoded": payload[1][:80]})

    report["avg_chars"] = round(total_chars / max(len(dataset), 1), 1)
    return report


def print_report(report):
    print("=" * 64)
    print(f"  DATASET : {report['name']}")
    print("=" * 64)
    print(f"  Volume total ............ {report['total']} echantillons")
    print(f"  Longueur moyenne ........ {report['avg_chars']} caracteres")
    print(f"  Doublons ................ {report['duplicates']}")
    print(f"  Champs vides ............ {report['empty_fields']}")
    print("  Formats detectes :")
    for fmt, count in report["formats"].most_common():
        print(f"      - {fmt:20s} {count}")
    print("-" * 64)
    print("  ANOMALIES DE SECURITE")
    print(f"    Trigger backdoor ...... {len(report['backdoor_samples'])} echantillon(s)")
    if report["backdoor_samples"]:
        print(f"        index : {report['backdoor_samples'][:20]}")
    print(f"    Credentials en clair .. {len(report['credential_samples'])} echantillon(s)")
    if report["credential_samples"]:
        print(f"        index : {report['credential_samples'][:20]}")
    print(f"    Payloads base64 ....... {len(report['base64_payloads'])}")
    for p in report["base64_payloads"][:5]:
        print(f"        [{p['index']}] {p['encoded']}... -> \"{p['decoded']}\"")
    print("=" * 64)


def clean_dataset(dataset, report):
    """Retire les echantillons empoisonnes et les doublons exacts."""
    poisoned = set(report["backdoor_samples"]) | set(report["credential_samples"])
    poisoned |= {p["index"] for p in report["base64_payloads"]}

    cleaned = []
    seen = set()
    removed_dupes = 0
    for idx, item in enumerate(dataset):
        if idx in poisoned:
            continue
        text = extract_text(item)
        if not text.strip():
            continue
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
        if digest in seen:
            removed_dupes += 1
            continue
        seen.add(digest)
        cleaned.append(item)

    return cleaned, {
        "removed_poisoned": len(poisoned),
        "removed_duplicates": removed_dupes,
        "kept": len(cleaned),
    }


def main():
    parser = argparse.ArgumentParser(description="Analyse et nettoyage des datasets herites.")
    parser.add_argument("path", help="Chemin du fichier JSON a analyser.")
    parser.add_argument("--clean", metavar="OUT", help="Ecrit une version nettoyee dans OUT.")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        sys.exit(f"[ERREUR] Fichier introuvable : {args.path}")

    if is_lfs_pointer(args.path):
        print("[AVERTISSEMENT] Ce fichier est un pointeur git-lfs, pas le contenu reel.")
        print("                Executez 'git lfs pull' pour recuperer les donnees,")
        print("                puis relancez ce script.")
        sys.exit(2)

    print(f"[{datetime.now():%H:%M:%S}] Chargement de {args.path} ...")
    dataset = load_dataset(args.path)
    if not isinstance(dataset, list):
        sys.exit("[ERREUR] Format attendu : liste JSON d'echantillons.")

    report = analyze(dataset, os.path.basename(args.path))
    print_report(report)

    if args.clean:
        cleaned, stats = clean_dataset(dataset, report)
        with open(args.clean, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        print()
        print(f"[NETTOYAGE] Echantillons empoisonnes retires .. {stats['removed_poisoned']}")
        print(f"[NETTOYAGE] Doublons retires .................. {stats['removed_duplicates']}")
        print(f"[NETTOYAGE] Echantillons conserves ............ {stats['kept']}")
        print(f"[NETTOYAGE] Fichier ecrit : {args.clean}")


if __name__ == "__main__":
    main()
