#!/usr/bin/env bash
# Aquest script instal·la sudo i configura l'usuari "salvadorrueda" per a tenir accés complet a sudo sense necessitat de contrasenya.

set -euo pipefail

USUARI_OBJECTIU="salvadorrueda"
FITXER_SUDOERS="/etc/sudoers.d/90-${USUARI_OBJECTIU}-full-access"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Error: executa aquest script com a root (per exemple, amb su -)."
    exit 1
fi

if [[ -r /etc/os-release ]]; then
    . /etc/os-release
    if [[ "${ID:-}" != "debian" || "${VERSION_ID:-}" != "12" ]]; then
        echo "Avís: aquest script està pensat per Debian 12."
        echo "Sistema detectat: ${PRETTY_NAME:-desconegut}"
    fi
fi

if ! id "${USUARI_OBJECTIU}" >/dev/null 2>&1; then
    echo "Error: l'usuari '${USUARI_OBJECTIU}' no existeix al sistema."
    exit 1
fi

echo "Instal·lant sudo..."
apt update
apt install -y sudo

echo "Assegurant l'existència del grup sudo..."
getent group sudo >/dev/null || groupadd sudo

echo "Afegint l'usuari ${USUARI_OBJECTIU} al grup sudo..."
usermod -aG sudo "${USUARI_OBJECTIU}"

echo "Configurant permisos complets de sudo sense contrasenya per a ${USUARI_OBJECTIU}..."
cat > "${FITXER_SUDOERS}" <<EOF
${USUARI_OBJECTIU} ALL=(ALL:ALL) NOPASSWD:ALL
EOF

chmod 440 "${FITXER_SUDOERS}"

if ! visudo -cf "${FITXER_SUDOERS}" >/dev/null; then
    echo "Error: configuració sudoers invàlida."
    exit 1
fi

echo "Configuració completada correctament."
echo "L'usuari ${USUARI_OBJECTIU} ja pot executar qualsevol comanda amb sudo, inclòs 'sudo su'."
