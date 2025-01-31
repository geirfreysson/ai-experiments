import click
import subprocess
import os
import nbformat

def run_shot_scraper(url, output_folder, output_image):
    """
    Run the shot-scraper command with the given URL and predefined JavaScript modifications,
    saving the output image with the specified name.
    """
    javascript_code = '''
    document.querySelector('h1.title').style.fontSize='2em';
    document.querySelector('.navbar-toggler-icon').style.display = 'none';
    document.querySelectorAll('section').forEach(el => el.style.display = 'none');
    document.querySelector('.navbar-brand-logo img').style.height='140px';
    document.querySelector('.navbar-brand-logo').style.marginTop='10px';
    document.querySelector('.quarto-title').style.marginTop='40px';
    document.querySelector('h1.title').style.top = "10px";
    document.querySelectorAll('p').forEach(el => el.style.display = 'none');
    document.querySelectorAll('li').forEach(el => el.style.display = 'none');
    document.querySelectorAll('pre').forEach(el => el.style.display = 'none');
    document.querySelectorAll('hr').forEach(el => el.style.display = 'none');
    document.querySelectorAll('div.cell').forEach(el => el.style.display = 'none');
    '''
    
    command = [
        "uv", "run", "shot-scraper", url,
        "-h", "418", "-w", "800",
        "--javascript", javascript_code,
        "-o", os.path.join(output_folder, output_image)
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        click.echo(f"Created screenshot for:https://geirfreysson.com/{url}".replace("_site/",""))
        return True
    except Exception as e:
        click.echo(f"Error executing shot-scraper: {e}", err=True)
        click.echo(f"Shot-scraper stderr:\n{e.stderr}", err=True)
        return False

def update_notebook_image_tag(notebook_path, image_name):
    """Update the notebook's first raw cell to include the image tag."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
            
        if notebook.cells and notebook.cells[0].cell_type == "raw":
            metadata = notebook.cells[0].source
            lines = metadata.split("\n")
            new_lines = []
            image_tag_found = False
            
            for line in lines:
                if line.strip().startswith("image:"):
                    new_lines.append(f"image: \"{image_name}\"")
                    image_tag_found = True
                else:
                    new_lines.append(line)
            
            # Ensure the image tag is added as the second-to-last line
            if not image_tag_found:
                if len(new_lines) > 0:
                    new_lines.insert(len(new_lines) - 1, f"image: \"{image_name}\"")
                else:
                    new_lines.append(f"image: \"{image_name}\"")
            
            notebook.cells[0].source = "\n".join(new_lines)
            
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
    except Exception as e:
        click.echo(f"Error updating notebook {notebook_path}: {e}", err=True)

def check_notebook_for_image_tag(notebook_path):
    """Check if the first raw cell of the notebook contains a non-empty image tag."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
            if notebook.cells and notebook.cells[0].cell_type == "raw":
                metadata = notebook.cells[0].source
                if "image:" in metadata:
                    lines = metadata.split("\n")
                    for line in lines:
                        if line.strip().startswith("image:"):
                            image_value = line.split(":", 1)[-1].strip().strip('"')
                            return bool(image_value)  # True if image is not empty
    except Exception as e:
        click.echo(f"Error checking notebook {notebook_path}: {e}", err=True)
    return False

@click.command()
@click.argument('base_folder', type=click.Path(exists=True), default=".")
def main(base_folder):
    """Loop through all folders in 'posts' and check for missing images."""
    posts_path = os.path.join(base_folder, "posts")
    
    for folder in os.listdir(posts_path):
        folder_path = os.path.join(posts_path, folder)
        if os.path.isdir(folder_path):
            notebook_path = os.path.join(folder_path, "index.ipynb")
            if os.path.exists(notebook_path):
                if not check_notebook_for_image_tag(notebook_path):
                    image_name = f"social-media-card.png"
                    site_url = os.path.join("_site/posts", folder, "index.html")
                    output_folder = os.path.join("./posts/", folder)
                    if run_shot_scraper(site_url, output_folder, image_name):
                        update_notebook_image_tag(notebook_path, image_name)
                    else:
                        click.echo(f"Shot-scraper stderr:\n{e.stderr}")

if __name__ == "__main__":
    main()
