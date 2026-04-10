#!/usr/bin/env bash

set -euo pipefail

VM_NAME="vu01"

usage() {
    cat <<'EOF'
Ús:
  ./launch_vu01.sh [--headless]

Aquest script inicia la màquina virtual "vu01" assignant-li la meitat de la RAM
disponible al sistema.

Opcions:
  --headless   Inicia la màquina virtual sense interfície gràfica (mode headless).
EOF
}

require_commands() {
    local command
    for command in VBoxManage awk grep; do
        if ! command -v "$command" >/dev/null 2>&1; then
            echo "Falta el comandament requerit: $command" >&2
            exit 1
        fi
    done
}

get_half_ram_mb() {
    local total_ram_kb half_ram_mb
    total_ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    half_ram_mb=$(( total_ram_kb / 1024 / 2 ))
    echo "${half_ram_mb}"
}

check_vm_exists() {
    if ! VBoxManage showvminfo "${VM_NAME}" >/dev/null 2>&1; then
        echo "Error: no s'ha trobat cap màquina virtual amb el nom '${VM_NAME}'." >&2
        exit 1
    fi
}

check_vm_not_running() {
    local state
    state=$(VBoxManage showvminfo "${VM_NAME}" --machinereadable | grep '^VMState=' | cut -d'"' -f2)
    if [[ "${state}" == "running" ]]; then
        echo "La màquina virtual '${VM_NAME}' ja està en execució." >&2
        exit 1
    fi
}

set_vm_memory() {
    local ram_mb="${1}"
    echo "Configurant la RAM de '${VM_NAME}' a ${ram_mb} MB..."
    VBoxManage modifyvm "${VM_NAME}" --memory "${ram_mb}"
}

create_snapshot() {
    local timestamp
    timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    echo "Creant la snapshot '${timestamp}' per a la màquina '${VM_NAME}'..."
    VBoxManage snapshot "${VM_NAME}" take "${timestamp}" --description "Snapshot automàtica abans d'iniciar"
}

start_vm() {
    local headless="${1}"
    if [[ "${headless}" == "true" ]]; then
        echo "Iniciant '${VM_NAME}' en mode headless..."
        VBoxManage startvm "${VM_NAME}" --type headless
    else
        echo "Iniciant '${VM_NAME}' amb interfície gràfica..."
        VBoxManage startvm "${VM_NAME}" --type gui
    fi
}

main() {
    local headless="false"

    for arg in "$@"; do
        case "${arg}" in
            --headless)
                headless="true"
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                echo "Opció desconeguda: ${arg}" >&2
                usage >&2
                exit 1
                ;;
        esac
    done

    require_commands
    check_vm_exists
    check_vm_not_running

    local half_ram_mb
    half_ram_mb=$(get_half_ram_mb)
    echo "RAM total detectada: $(( half_ram_mb * 2 )) MB → assignant ${half_ram_mb} MB a '${VM_NAME}'."

    set_vm_memory "${half_ram_mb}"
    create_snapshot
    start_vm "${headless}"

    echo "Màquina virtual '${VM_NAME}' iniciada correctament."
}

main "$@"
