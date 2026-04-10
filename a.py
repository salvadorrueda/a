#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Scripts")
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return {}


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(script, keyword):
    path = os.path.join(SCRIPT_DIR, script)
    if not os.path.isfile(path):
        print(f"Error: no se encuentra el script '{script}' en {SCRIPT_DIR}")
        sys.exit(1)
    tasks = load_tasks()
    tasks[keyword] = script
    save_tasks(tasks)
    print(f"Tarea añadida: '{keyword}' -> {script}")


def remove_task(keyword):
    tasks = load_tasks()
    if keyword not in tasks:
        print(f"Error: no existe ninguna tarea con la palabra clave '{keyword}'")
        sys.exit(1)
    del tasks[keyword]
    save_tasks(tasks)
    print(f"Tarea eliminada: '{keyword}'")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No hay tareas registradas.")
        return
    for keyword, script in sorted(tasks.items()):
        print(f"  {keyword}  ->  {script}")


def run_task(keyword):
    tasks = load_tasks()
    if keyword not in tasks:
        print(f"Error: no existe ninguna tarea con la palabra clave '{keyword}'")
        sys.exit(1)
    script = tasks[keyword]
    path = os.path.join(SCRIPT_DIR, script)
    if not os.path.isfile(path):
        print(f"Error: el script '{path}' ya no existe")
        sys.exit(1)
    os.execvp("bash", ["bash", path])


def main():
    parser = argparse.ArgumentParser(
        description="Gestor de tareas automatizadas"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--add", nargs=2, metavar=("SCRIPT", "PALABRA_CLAVE"),
                       help="Registra un script con una palabra clave")
    group.add_argument("--remove", metavar="PALABRA_CLAVE",
                       help="Elimina una tarea registrada")
    group.add_argument("--list", action="store_true",
                       help="Lista todas las tareas registradas")
    parser.add_argument("keyword", nargs="?",
                        help="Palabra clave de la tarea a ejecutar")

    args = parser.parse_args()

    if args.add:
        add_task(args.add[0], args.add[1])
    elif args.remove:
        remove_task(args.remove)
    elif args.list:
        list_tasks()
    elif args.keyword:
        run_task(args.keyword)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
