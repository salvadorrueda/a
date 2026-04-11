#!/bin/bash
# Aquest script instal·la Docker Engine a Debian 12 o 13.

# Comprovar si s'executa com a root
if [ "$EUID" -ne 0 ]; then
  exec sudo bash "$0" "$@"
fi

echo "Eliminant versions antigues de Docker..."
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
  apt-get remove -y $pkg
done

echo "Instal·lant dependències prèvies..."
apt-get update
apt-get install -y ca-certificates curl gnupg

# Configurar la clau GPG de Docker
echo "Configurant la clau GPG de Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
chmod a+r /etc/apt/keyrings/docker.gpg

# Configurar el repositori
echo "Configurant el repositori de Docker..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Instal·lant Docker Engine..."
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Afegir l'usuari actual al grup docker (si existeix SUDO_USER)
if [ -n "$SUDO_USER" ]; then
  echo "Afegint l'usuari $SUDO_USER al grup docker..."
  usermod -aG docker $SUDO_USER
fi

echo "Verificant la instal·lació..."
docker --version
docker compose version

echo "Instal·lació de Docker finalitzada."
echo "Recorda tancar la sessió i tornar a entrar perquè els canvis de grup tinguin efecte."
