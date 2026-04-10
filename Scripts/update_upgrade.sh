#!/usr/bin/env bash

set -euo pipefail

echo "Actualitzant llista de paquets..."
sudo apt update

echo "Actualitzant paquets instal·lats..."
sudo apt upgrade -y

echo "Eliminant paquets obsolets..."
sudo apt autoremove -y

echo "Netejant la caché de paquets..."
sudo apt autoclean

echo "Sistema actualitzat correctament."
