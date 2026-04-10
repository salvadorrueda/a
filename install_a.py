#!/usr/bin/env python3

import os
import shutil
import stat
import sys
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

BIN_DIR = os.path.expanduser("~/.local/bin")
DATA_DIR = os.path.expanduser("~/.local/share/a")
SCRIPTS_DST = os.path.join(DATA_DIR, "Scripts")
TASKS_DST = os.path.join(DATA_DIR, "tasks.json")
BIN_DST = os.path.join(BIN_DIR, "a")

SCRIPTS_SRC = os.path.join(REPO_DIR, "Scripts")
TASKS_SRC = os.path.join(REPO_DIR, "tasks.json")
A_SRC = os.path.join(REPO_DIR, "a.py")


def ensure_dirs():
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DST, exist_ok=True)


def install_main_script():
    with open(A_SRC) as f:
        content = f.read()

    # Ajusta les rutes constants perquè apuntin a la ubicació d'instal·lació
    content = content.replace(
        'SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Scripts")',
        f'SCRIPT_DIR = os.path.expanduser("~/.local/share/a/Scripts")',
    )
    content = content.replace(
        'TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")',
        f'TASKS_FILE = os.path.expanduser("~/.local/share/a/tasks.json")',
    )

    with open(BIN_DST, "w") as f:
        f.write(content)

    # Fa el fitxer executable
    current = os.stat(BIN_DST).st_mode
    os.chmod(BIN_DST, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  Instal·lat: {BIN_DST}")


def install_scripts():
    scripts = [
        f for f in os.listdir(SCRIPTS_SRC)
        if os.path.isfile(os.path.join(SCRIPTS_SRC, f))
    ]
    for script in scripts:
        src = os.path.join(SCRIPTS_SRC, script)
        dst = os.path.join(SCRIPTS_DST, script)
        shutil.copy2(src, dst)
        current = os.stat(dst).st_mode
        os.chmod(dst, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  Script copiat: {dst}")
    if not scripts:
        print("  Cap script trobat a Scripts/")


def install_tasks():
    if not os.path.exists(TASKS_SRC):
        print("  No s'ha trobat tasks.json, es crearà quan s'afegeixi la primera tasca.")
        return

    if not os.path.exists(TASKS_DST):
        shutil.copy2(TASKS_SRC, TASKS_DST)
        print(f"  Tasques copiades: {TASKS_DST}")
        return

    backup = f"{TASKS_DST}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(TASKS_DST, backup)
    print(f"  Backup creat: {backup}")

    update_tasks = False
    if sys.stdin.isatty():
        reply = input("  Ja existeix tasks.json. Vols actualitzar-lo amb la versió del repositori? [s/N]: ").strip().lower()
        update_tasks = reply in {"s", "si", "sí", "y", "yes"}
    else:
        print("  Entorn no interactiu: es manté el tasks.json local.")

    if update_tasks:
        shutil.copy2(TASKS_SRC, TASKS_DST)
        print(f"  Tasques actualitzades: {TASKS_DST}")
    else:
        print("  Es manté el tasks.json local (sense canvis).")


def check_path():
    path_dirs = os.environ.get("PATH", "").split(":")
    if BIN_DIR not in path_dirs:
        print()
        print(f"AVÍS: '{BIN_DIR}' no és al PATH.")
        print("Afegeix aquesta línia al teu ~/.bashrc o ~/.zshrc:")
        print(f'  export PATH="$HOME/.local/bin:$PATH"')
        print("Després executa: source ~/.bashrc")


def main():
    print("Instal·lant 'a'...")
    ensure_dirs()
    install_main_script()
    install_scripts()
    install_tasks()
    check_path()
    print()
    print("Instal·lació completada. Ara pots usar 'a' des de qualsevol terminal.")


if __name__ == "__main__":
    main()
