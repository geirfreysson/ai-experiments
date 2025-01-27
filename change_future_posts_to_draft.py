import os
import json
import nbformat
from datetime import datetime

POSTS_DIR = "posts"
DATE_FORMAT = "%Y-%m-%d"

def update_draft_status():
    today = datetime.today().date()
    
    for root, _, files in os.walk(POSTS_DIR):
        if "index.ipynb" in files:
            notebook_path = os.path.join(root, "index.ipynb")
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            
            # Check if the first cell is a raw cell and contains metadata
            if nb.cells and nb.cells[0].cell_type == "raw":
                raw_content = nb.cells[0].source.strip()
                if raw_content.startswith("---") and raw_content.endswith("---"):
                    metadata_lines = raw_content.split("\n")[1:-1]  # Remove the surrounding ---
                    metadata = {}
                    
                    for line in metadata_lines:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        #if key == "categories":
                        #    value = [cat.strip() for cat in value.strip("[]").split(",")]
                        if key == "draft" or key == "publish":
                            value = value.lower() == "true"
                        metadata[key] = value
                    
                    # Check date and update draft status only if publish is true
                    if "date" in metadata:
                        post_date = datetime.strptime(metadata["date"], DATE_FORMAT).date()
                        if post_date > today:
                            metadata["draft"] = True
                        elif metadata.get("publish", False):
                            metadata["draft"] = False
                            
                        # Rebuild raw cell content
                        updated_raw_content = "---\n" + "\n".join(
                            f"{k}: {json.dumps(v) if isinstance(v, list) else v}"
                            for k, v in metadata.items()
                        ) + "\n---"
                        
                        nb.cells[0].source = updated_raw_content
                        
                        # Save updated notebook
                        with open(notebook_path, "w", encoding="utf-8") as f:
                            nbformat.write(nb, f)
                        print(f"Updated draft status in: {notebook_path}")

if __name__ == "__main__":
    if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
        print("Not fixing draft status")
        exit()
    else:
        update_draft_status()
