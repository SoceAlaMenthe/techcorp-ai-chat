#!/usr/bin/env python3
"""
Health-check du serveur d'inference Ollama — filiere INFRA.

Verifie :
  - que l'API repond (/api/version),
  - que le modele attendu est bien charge (/api/tags),
  - qu'une inference simple aboutit (/api/generate).

Usage :
    python healthcheck.py
    python healthcheck.py --url http://localhost:11434 --model techcorp-finance
"""

import argparse
import json
import sys
import time
import urllib.request


def get(url, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def post(url, payload, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:11434")
    p.add_argument("--model", default="techcorp-finance")
    args = p.parse_args()
    base = args.url.rstrip("/")
    ok = True

    print(f"[1/3] Version API ({base}/api/version) ...", end=" ")
    try:
        v = get(f"{base}/api/version")
        print(f"OK - ollama {v.get('version', '?')}")
    except Exception as e:  # noqa: BLE001
        print(f"ECHEC ({e})")
        print("      -> Le serveur ne repond pas. Lancez 'ollama serve'.")
        sys.exit(1)

    print(f"[2/3] Modele '{args.model}' charge ...", end=" ")
    try:
        tags = get(f"{base}/api/tags")
        names = [m.get("name", "") for m in tags.get("models", [])]
        if any(args.model in n for n in names):
            print("OK")
        else:
            print(f"ABSENT (modeles: {names or 'aucun'})")
            print(f"      -> Creez-le : ollama create {args.model} -f Modelfile")
            ok = False
    except Exception as e:  # noqa: BLE001
        print(f"ECHEC ({e})")
        ok = False

    print("[3/3] Inference de test ...", end=" ")
    try:
        t0 = time.time()
        resp = post(f"{base}/api/generate",
                    {"model": args.model, "prompt": "Say READY in one word.", "stream": False})
        dt = time.time() - t0
        text = resp.get("response", "").strip()
        print(f"OK - {dt:.1f}s - reponse: {text[:60]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"ECHEC ({e})")
        ok = False

    print("\nRESULTAT :", "SERVEUR OPERATIONNEL" if ok else "PROBLEME DETECTE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
