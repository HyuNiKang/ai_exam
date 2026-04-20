import os
import json
import glob

placeholder = "### !!!!!!!!!!!!코드를 작성하세요!!!!!!!!!!!!"
replacement = "## Write Answer"

ipynb_files = glob.glob("**/*.ipynb", recursive=True)

for filepath in ipynb_files:
    with open(filepath, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    modified = False
    for cell in notebook.get("cells", []):
        source = cell.get("source", [])
        new_source = []
        for line in source:
            new_line = line.replace(placeholder, replacement)
            if new_line != line:
                modified = True
            new_source.append(new_line)
        cell["source"] = new_source

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(notebook, f, ensure_ascii=False, indent=1)
        print(f"Updated: {filepath}")
    else:
        print(f"No changes: {filepath}")
