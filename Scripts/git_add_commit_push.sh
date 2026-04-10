#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Ús:
  ./git_add_commit_push.sh "missatge del commit"

Exemple:
  ./git_add_commit_push.sh "Actualitza scripts de manteniment"
EOF
}

if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "Error: el directori actual no és un repositori Git."
    exit 1
fi

comentari_commit="$*"

echo "Afegint canvis al commit..."
git add -A

echo "Creant commit..."
git commit -m "$comentari_commit"

echo "Enviant canvis al remot..."
git push

echo "Procés completat correctament."