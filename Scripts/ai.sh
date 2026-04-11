#!/bin/bash
# ai.sh — Executa l'eina d'IA dins un contenidor Docker.
#
# Proveïdors suportats: claude, chatgpt, gemini, ollama
#
# Ús:
#   a ai "la teva pregunta"
#   a ai -p claude "la teva pregunta"
#   a ai -p chatgpt -m gpt-4o "la teva pregunta"
#   a ai -p ollama -m mistral "la teva pregunta"
#   echo "pregunta" | a ai -p gemini
#
# Variables d'entorn necessàries:
#   ANTHROPIC_API_KEY    — clau per a Claude
#   OPENAI_API_KEY       — clau per a ChatGPT
#   GOOGLE_API_KEY       — clau per a Gemini
#   AI_DEFAULT_PROVIDER  — proveïdor per defecte (claude|chatgpt|gemini|ollama)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="ai-cli"

# Construir la imatge Docker si no existeix
if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
    echo "Construint la imatge Docker '$IMAGE_NAME' (només cal fer-ho el primer cop)..." >&2
    docker build -t "$IMAGE_NAME" -f "$SCRIPT_DIR/Dockerfile.ai" "$SCRIPT_DIR" >&2
fi

# Executar el contenidor:
#   --rm           → elimina el contenidor en acabar
#   --network host → permet accedir a Ollama a localhost:11434
#   -i             → manté stdin obert (necessari per a pipes)
exec docker run --rm \
    --network host \
    -i \
    -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e GOOGLE_API_KEY="${GOOGLE_API_KEY:-}" \
    -e AI_DEFAULT_PROVIDER="${AI_DEFAULT_PROVIDER:-}" \
    "$IMAGE_NAME" "$@"
