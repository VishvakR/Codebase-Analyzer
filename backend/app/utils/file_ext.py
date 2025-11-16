import os
from pathlib import Path
import ast

IGNORED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
ALLOWED_EXTS = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts'}

def list_files(repo_path: str):
    repo_path = Path(repo_path)
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in ALLOWED_EXTS:
                yield str(p.relative_to(repo_path)), str(p)

def read_file(path: str):
    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
        return fh.read()

def extract_python_symbols(file_path: str):
    source = read_file(file_path)
    try:
        tree = ast.parse(source)
    except Exception:
        return [], source
    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = getattr(node, 'lineno', None)
            end = getattr(node, 'end_lineno', None)
            symbols.append({'name': getattr(node, 'name', None), 'start_line': start, 'end_line': end})
    return symbols, source


def is_allowed_file(filename):
    return os.path.splitext(filename)[1] in ALLOWED_EXTS

def generate_tree(start_path, prefix="", lines=None):
    if lines is None:
        lines = []

    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        return lines

    filtered_items = []
    for item in items:
        path = os.path.join(start_path, item)

        if os.path.isdir(path) and item in IGNORED_DIRS:
            continue

        if os.path.isfile(path) and not is_allowed_file(item):
            continue

        filtered_items.append(item)

    pointers = ["├── "] * (len(filtered_items) - 1) + ["└── "] if filtered_items else []

    for pointer, item in zip(pointers, filtered_items):
        path = os.path.join(start_path, item)
        lines.append(prefix + pointer + item)

        if os.path.isdir(path):
            extension = "│   " if pointer == "├── " else "    "
            generate_tree(path, prefix + extension, lines)

    return lines