"""Check source structure without executing analysis code."""
import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
count = 0
for path in root.rglob("*"):
    if any(part in {".git", ".venv", "data", "outputs", "__pycache__"} for part in path.parts):
        continue
    if path.suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count += 1
    elif path.suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix == ".ipynb":
        notebook = json.loads(path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4, path
        language = notebook.get("metadata", {}).get("kernelspec", {}).get("language", "python").lower()
        for index, cell in enumerate(notebook["cells"]):
            assert isinstance(cell["source"], list), (path, index)
            if cell["cell_type"] == "code":
                assert cell.get("outputs", []) == [], (path, index)
                assert cell.get("execution_count") is None, (path, index)
                if language == "python":
                    ast.parse("".join(cell["source"]), filename=f"{path}:cell {index + 1}")
        count += 1
print(f"Static source validation passed: {count} Python/notebook files. No analysis was executed.")
