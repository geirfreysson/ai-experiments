import os
import nbformat
from datetime import datetime

POSTS_DIR = "posts"
DATE_FORMAT = "%Y-%m-%d"

def top_level_value(lines, key):
    for line in lines:
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"')
    return None

def update_draft_status():
    today = datetime.today().date()

    for root, _, files in os.walk(POSTS_DIR):
        if "index.ipynb" not in files:
            continue
        notebook_path = os.path.join(root, "index.ipynb")
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # Check if the first cell is a raw cell and contains metadata
        if not (nb.cells and nb.cells[0].cell_type == "raw"):
            continue
        raw_content = nb.cells[0].source.strip()
        if not (raw_content.startswith("---") and raw_content.endswith("---")):
            continue

        lines = raw_content.split("\n")

        date_str = top_level_value(lines, "date")
        if date_str is None:
            continue
        post_date = datetime.strptime(date_str, DATE_FORMAT).date()

        publish = (top_level_value(lines, "publish") or "").lower() == "true"
        current_draft = top_level_value(lines, "draft")
        if post_date > today:
            new_draft = "true"
        elif publish:
            new_draft = "false"
        else:
            new_draft = current_draft

        if new_draft is None or new_draft == current_draft:
            continue

        # Patch only the draft line in place, preserving every other line
        # (including nested keys like execute/freeze) exactly as written.
        updated_lines = [
            f'draft: "{new_draft}"' if line.startswith("draft:") else line
            for line in lines
        ]
        nb.cells[0].source = "\n".join(updated_lines)

        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        print(f"Updated draft status in: {notebook_path}")

if __name__ == "__main__":
    if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
        print("Not fixing draft status")
        exit()
    else:
        update_draft_status()
