#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import stat
import sys

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Scripts")
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def ensure_script_dir():
    os.makedirs(SCRIPT_DIR, exist_ok=True)


def make_executable(path):
    current_mode = os.stat(path).st_mode
    os.chmod(path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def resolve_script_source(script):
    expanded_path = os.path.abspath(os.path.expanduser(script))
    if os.path.isfile(expanded_path):
        return expanded_path

    stored_path = os.path.join(SCRIPT_DIR, script)
    if os.path.isfile(stored_path):
        return stored_path

    stored_basename_path = os.path.join(SCRIPT_DIR, os.path.basename(script))
    if os.path.isfile(stored_basename_path):
        return stored_basename_path

    return None


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return {}


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(script, keyword):
    source_path = resolve_script_source(script)
    if source_path is None:
        print(f"Error: no se encuentra el script '{script}'")
        sys.exit(1)

    ensure_script_dir()
    stored_script = os.path.basename(source_path)
    stored_path = os.path.join(SCRIPT_DIR, stored_script)

    if os.path.abspath(source_path) != os.path.abspath(stored_path):
        shutil.copy2(source_path, stored_path)

    make_executable(stored_path)

    tasks = load_tasks()
    tasks[keyword] = stored_script
    save_tasks(tasks)
    print(f"Tarea añadida: '{keyword}' -> {stored_script}")


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


def run_task(keyword, script_args=None):
    if script_args is None:
        script_args = []

    tasks = load_tasks()
    if keyword not in tasks:
        print(f"Error: no existe ninguna tarea con la palabra clave '{keyword}'")
        sys.exit(1)
    script = tasks[keyword]
    path = os.path.join(SCRIPT_DIR, script)
    if not os.path.isfile(path):
        print(f"Error: el script '{path}' ya no existe")
        sys.exit(1)
    os.execvp("bash", ["bash", path, *script_args])


def build_parser():
    parser = argparse.ArgumentParser(description="Gestor de tareas automatizadas")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Registra un script con una palabra clave")
    add_parser.add_argument("script", help="Ruta o nombre del script")
    add_parser.add_argument("keyword", help="Palabra clave para ejecutar la tarea")

    subparsers.add_parser("list", help="Lista todas las tareas registradas")

    remove_parser = subparsers.add_parser("remove", help="Elimina una tarea registrada")
    remove_parser.add_argument("keyword", help="Palabra clave de la tarea")

    run_parser = subparsers.add_parser("run", help="Ejecuta una tarea registrada")
    run_parser.add_argument("keyword", help="Palabra clave de la tarea")
    run_parser.add_argument("script_args", nargs=argparse.REMAINDER,
                            help="Argumentos extra para el script")

    return parser


def main():
    parser = build_parser()
    argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return

    known_commands = {"add", "list", "remove", "run", "-h", "--help"}
    if argv[0] not in known_commands and not argv[0].startswith("-"):
        run_task(argv[0], argv[1:])
        return

    args = parser.parse_args(argv)

    if args.command == "add":
        add_task(args.script, args.keyword)
    elif args.command == "remove":
        remove_task(args.keyword)
    elif args.command == "list":
        list_tasks()
    elif args.command == "run":
        run_task(args.keyword, args.script_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
