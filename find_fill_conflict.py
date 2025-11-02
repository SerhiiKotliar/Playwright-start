import os
import re
import ast

root_dir = os.getcwd()

# === Регулярка для прямого поиска fill-переопределений ===
pattern = re.compile(
    r'\b(from\s+textwrap\s+import\s+fill|def\s+fill\s*\(|fill\s*=)(?!.*\.)'
)

found_conflicts = []

print(f"🔍 Поиск возможных конфликтов 'fill' в Python-файлах внутри {root_dir}...\n")

for root, _, files in os.walk(root_dir):
    for file in files:
        if not file.endswith(".py"):
            continue
        path = os.path.join(root, file)
        if ".venv" in path or "site-packages" in path:
            continue  # пропускаем окружение
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            continue

        for i, line in enumerate(lines, start=1):
            if ".fill(" in line:
                continue
            if pattern.search(line):
                found_conflicts.append((path, i, line.strip()))

# === Если прямых совпадений нет, анализируем импорты ===
if not found_conflicts:
    print("⚙️  Прямых конфликтов не найдено. Проверяю импортированные файлы...\n")

    imported_files = set()
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and ".venv" not in root:
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=path)
                except Exception:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module == "textwrap":
                        for alias in node.names:
                            if alias.name == "fill":
                                found_conflicts.append((path, node.lineno, f"from textwrap import fill"))
                    elif isinstance(node, ast.ImportFrom):
                        imported_files.add(node.module)

# === Вывод результата ===
if found_conflicts:
    for path, line, text in found_conflicts:
        print(f"🚨 Найдено возможное переопределение в файле:\n  {path}:{line}: {text}\n")
else:
    print("✅ Конфликтов и импортов textwrap.fill не найдено.")

print("\n🔎 Проверка завершена.")
