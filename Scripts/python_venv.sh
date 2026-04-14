#!/usr/bin/env bash
# Aquest script comprova si existeix l'entorn virtual "venv".
# Si no existeix, el crea i després l'activa.

set -euo pipefail

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Avís: per mantenir l'entorn actiu al shell actual, executa:"
  echo "source Scripts/python_venv.sh"
fi

if [[ ! -d "venv" ]]; then
  echo "No s'ha trobat l'entorn virtual 'venv'. Creant-lo..."

  if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: no s'ha trobat 'python3' al sistema." >&2
    exit 1
  fi

  python3 -m venv venv
  echo "Entorn virtual 'venv' creat correctament."
else
  echo "L'entorn virtual 'venv' ja existeix."
fi

echo "Activant l'entorn virtual..."
source venv/bin/activate