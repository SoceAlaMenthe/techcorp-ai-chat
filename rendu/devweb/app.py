#!/usr/bin/env python3
"""
Interface de chat — Assistant financier TechCorp (filière DEV WEB).

Front Streamlit connecté au serveur d'inférence Ollama déployé par l'équipe INFRA.
Fonctionnalités :
  - conversation en temps réel (streaming),
  - historique de la conversation affiché,
  - indicateur d'état de connexion au serveur (connecté / déconnecté),
  - configuration de l'URL et du modèle depuis la barre latérale.

Lancement : voir run.ps1 / run.sh (une commande).
"""

import json
import os
import urllib.error
import urllib.request

import streamlit as st

DEFAULT_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "techcorp-finance")

st.set_page_config(page_title="TechCorp — Assistant financier", page_icon="💼", layout="centered")


def check_server(url):
    """Retourne (connecte: bool, version: str|None)."""
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/api/version", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
        return True, data.get("version")
    except Exception:  # noqa: BLE001
        return False, None


def list_models(url):
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/api/tags", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:  # noqa: BLE001
        return []


def stream_chat(url, model, messages):
    """Interroge /api/chat en streaming ; yield les fragments de texte."""
    payload = json.dumps({"model": model, "messages": messages, "stream": True}).encode("utf-8")
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            chunk = json.loads(line)
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
            if chunk.get("done"):
                break


# --- État de session --------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Barre latérale : configuration + état ----------------------------------
with st.sidebar:
    st.header("Configuration")
    url = st.text_input("Serveur d'inférence", DEFAULT_URL)
    connected, version = check_server(url)

    if connected:
        st.success(f"Connecté — Ollama {version or ''}".strip())
    else:
        st.error("Déconnecté")
        st.caption("Vérifiez que l'équipe INFRA a démarré le serveur (`ollama serve`).")

    models = list_models(url)
    if models:
        default_idx = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
        model = st.selectbox("Modèle", models, index=default_idx)
    else:
        model = st.text_input("Modèle", DEFAULT_MODEL)

    st.divider()
    if st.button("Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("TechCorp Industries — Assistant financier interne")

# --- Zone principale --------------------------------------------------------
st.title("💼 Assistant financier TechCorp")

status_badge = "🟢 Connecté" if connected else "🔴 Déconnecté"
st.caption(f"Serveur : {url}  ·  Modèle : {model}  ·  {status_badge}")

# Historique.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Saisie utilisateur.
prompt = st.chat_input("Posez une question financière…", disabled=not connected)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        try:
            for token in stream_chat(url, model, st.session_state.messages):
                full += token
                placeholder.markdown(full + "▌")
            placeholder.markdown(full)
        except urllib.error.URLError:
            full = "⚠️ Impossible de joindre le serveur d'inférence. Vérifiez la connexion."
            placeholder.error(full)
        except Exception as e:  # noqa: BLE001
            full = f"⚠️ Erreur : {e}"
            placeholder.error(full)

    st.session_state.messages.append({"role": "assistant", "content": full})

if not connected:
    st.info(
        "Le serveur d'inférence n'est pas joignable. Démarrez-le côté INFRA "
        "(`ollama serve` puis `ollama create techcorp-finance -f Modelfile`), "
        "ou ajustez l'URL dans la barre latérale."
    )
