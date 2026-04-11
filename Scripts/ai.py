#!/usr/bin/env python3
# ai.py — Eina de línia de comandes per preguntar a proveïdors d'IA.
#
# Proveïdors suportats: claude, chatgpt, gemini, ollama
#
# Aquest script s'executa dins d'un contenidor Docker (vegeu ai.sh).
#
# Variables d'entorn necessàries (al sistema amfitrió, no dins el contenidor):
#   ANTHROPIC_API_KEY    — clau per a Claude (Anthropic)
#   OPENAI_API_KEY       — clau per a ChatGPT (OpenAI)
#   GOOGLE_API_KEY       — clau per a Gemini (Google)
#   AI_DEFAULT_PROVIDER  — proveïdor per defecte (claude|chatgpt|gemini|ollama)
#
# Ús:
#   a ai "la teva pregunta"
#   a ai -p claude "la teva pregunta"
#   a ai -p ollama -m llama3 "la teva pregunta"
#   echo "pregunta" | a ai -p gemini

import argparse
import os
import sys

PROVEIDOR_PER_DEFECTE = "claude"

MODELS_PER_DEFECTE = {
    "claude":  "claude-sonnet-4-6",
    "chatgpt": "gpt-4o",
    "gemini":  "gemini-1.5-pro",
    "ollama":  "llama3",
}

OLLAMA_URL = "http://localhost:11434"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Pregunta a proveïdors d'IA des de la línia de comandes"
    )
    parser.add_argument(
        "pregunta",
        nargs="?",
        default=None,
        help="La pregunta a fer a la IA",
    )
    parser.add_argument(
        "-p", "--proveidor",
        choices=["claude", "chatgpt", "gemini", "ollama"],
        default=None,
        help="Proveïdor d'IA a utilitzar (per defecte: AI_DEFAULT_PROVIDER o claude)",
    )
    parser.add_argument(
        "-m", "--model",
        default=None,
        help="Model específic a utilitzar (sobreescriu el model per defecte del proveïdor)",
    )
    return parser


def obtenir_pregunta(args):
    if args.pregunta:
        return args.pregunta
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("Error: cal proporcionar una pregunta com a argument o per stdin.", file=sys.stderr)
    print("  Exemple: a ai \"Quina és la capital de Catalunya?\"", file=sys.stderr)
    sys.exit(1)


def obtenir_proveidor(args):
    if args.proveidor:
        return args.proveidor
    return os.environ.get("AI_DEFAULT_PROVIDER", PROVEIDOR_PER_DEFECTE)


def requerir_clau(env_var, nom_proveidor):
    clau = os.environ.get(env_var)
    if not clau:
        print(
            f"Error: cal definir la variable d'entorn {env_var} per usar {nom_proveidor}.",
            file=sys.stderr,
        )
        print(f"  Exemple: export {env_var}='la-teva-clau'", file=sys.stderr)
        sys.exit(1)
    return clau


def preguntar_claude(pregunta, model):
    import anthropic
    clau = requerir_clau("ANTHROPIC_API_KEY", "Claude")
    client = anthropic.Anthropic(api_key=clau)
    with client.messages.stream(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": pregunta}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


def preguntar_chatgpt(pregunta, model):
    import openai
    clau = requerir_clau("OPENAI_API_KEY", "ChatGPT")
    client = openai.OpenAI(api_key=clau)
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": pregunta}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()


def preguntar_gemini(pregunta, model):
    import google.generativeai as genai
    clau = requerir_clau("GOOGLE_API_KEY", "Gemini")
    genai.configure(api_key=clau)
    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(pregunta, stream=True)
    for chunk in response:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


def preguntar_ollama(pregunta, model):
    import json
    import urllib.request
    payload = json.dumps({
        "model": model,
        "prompt": pregunta,
        "stream": True,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if line:
                    data = json.loads(line.decode())
                    text = data.get("response", "")
                    if text:
                        print(text, end="", flush=True)
                    if data.get("done"):
                        break
    except OSError:
        print(f"\nError: no s'ha pogut connectar amb Ollama a {OLLAMA_URL}.", file=sys.stderr)
        print("  Comprova que Ollama estigui en execució: ollama serve", file=sys.stderr)
        sys.exit(1)
    print()


PROVEIDORS = {
    "claude":  preguntar_claude,
    "chatgpt": preguntar_chatgpt,
    "gemini":  preguntar_gemini,
    "ollama":  preguntar_ollama,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    pregunta = obtenir_pregunta(args)
    proveidor = obtenir_proveidor(args)
    model = args.model or MODELS_PER_DEFECTE[proveidor]

    try:
        PROVEIDORS[proveidor](pregunta, model)
    except KeyboardInterrupt:
        print("\nInterromput.", file=sys.stderr)
        sys.exit(130)
    except ImportError as e:
        # Extreu el nom del paquet del missatge d'error
        msg = str(e)
        paquet = msg.split("'")[1] if "'" in msg else msg
        print(f"\nError: manca el paquet Python '{paquet}'.", file=sys.stderr)
        print(f"  Instal·la'l amb: pip3 install {paquet} --break-system-packages", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
