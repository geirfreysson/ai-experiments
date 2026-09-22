import re
from pathlib import Path

import nbformat

POSTS_DIR = Path("posts")
SITE_POSTS_DIR = Path("_site/posts")
PLACEHOLDER_RE = re.compile(r'(<span class="post-number">)\d+(</span>)')


def top_level_value(lines, key):
    for line in lines:
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"')
    return None


def published_posts():
    posts = []
    for notebook_path in POSTS_DIR.glob("*/index.ipynb"):
        nb = nbformat.read(notebook_path, as_version=4)
        if not (nb.cells and nb.cells[0].cell_type == "raw"):
            continue
        raw = nb.cells[0].source.strip()
        # Some raw cells contain the whole post body after the closing
        # "---", so only isolate the frontmatter between the first two
        # delimiters rather than requiring the cell to end with "---".
        if not raw.startswith("---"):
            continue
        parts = raw.split("---", 2)
        if len(parts) < 3:
            continue
        lines = parts[1].strip("\n").split("\n")

        date_str = top_level_value(lines, "date")
        if date_str is None:
            continue
        draft = (top_level_value(lines, "draft") or "").lower() == "true"
        if draft:
            continue

        html_file = SITE_POSTS_DIR / notebook_path.parent.name / "index.html"
        if html_file.exists():
            posts.append((date_str, html_file))

    posts.sort(key=lambda item: item[0])
    return posts


def assign_post_numbers():
    for i, (_, html_file) in enumerate(published_posts(), start=1):
        number = f"{i:02d}"
        text = html_file.read_text(encoding="utf-8")
        updated = PLACEHOLDER_RE.sub(rf"\g<1>{number}\g<2>", text)
        if updated != text:
            html_file.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    if SITE_POSTS_DIR.exists():
        assign_post_numbers()
