# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "bs4",
#     "click",
#     "ollama",
#     "nbformat",
#     "requests",
# ]
# ///

import click
import os
import datetime
import requests
from bs4 import BeautifulSoup
import ollama
import nbformat as nbf

# Initialize Ollama with the default model
#ollama = Ollama(model="llama3")

# Define the prompt template
prompt = """
I will provide a block of HTML content extracted using Beautiful Soup.

Please provide a **concise three-sentence summary** of the blog post:
1. The first sentence should describe the **theme** of the blog post.
2. The second sentence should explain **what the post outlines or covers**.
3. The third sentence should describe the **result or conclusion** of the blog post.

HTML content:
"""

# Helper function to generate the next Sunday date
def next_sunday():
    today = datetime.date.today()
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    return today + datetime.timedelta(days=days_until_sunday)

# Helper function to slugify a title
def slugify(title):
    return "-".join(title.lower().split())


# Command to create a new blog post
@click.group()
def cli():
    pass

@cli.command()
@click.argument("title")
@click.option("--url", default=None, help="URL to fetch and summarize")
@click.option("--model", default="llama3.1", help="What ollama model to use")
def new(title, url, model):
    # Create the folder name using next Sunday's date and the slugified title
    post_date = next_sunday().strftime("%Y-%m-%d")
    folder_name = f"posts/{post_date}-{slugify(title)}"
    os.makedirs(folder_name, exist_ok=True)

    # Create the index.ipynb file with metadata
    nb = nbf.v4.new_notebook()

    # Add the raw cell with metadata
    metadata = f"""---\ntitle: "{title}"\ndate: "{post_date}"\ndraft: "true"\npublish: "false"\nimage: "" \ncallout-appearance: simple\ncategories: []\n---\n"""
    nb.cells.append(nbf.v4.new_raw_cell(metadata))

    # If a URL is provided, fetch the page and summarize it
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the main content of the page (ignoring headers, footers, etc.)
            for tag in soup(['header', 'footer', 'nav', 'aside']):
                tag.decompose()
            content = soup.get_text()

            # Use Ollama to generate a summary
            summary = ollama.generate(model=model, prompt=prompt + content)
            
            # Add the summary as a markdown cell
            nb.cells.append(nbf.v4.new_markdown_cell(summary['response']))

        except requests.exceptions.RequestException as e:
            click.echo(f"Error fetching the URL: {e}")

    # Write the notebook to the index.ipynb file
    with open(f"{folder_name}/index.ipynb", "w") as f:
        nbf.write(nb, f)

    click.echo(f"Blog post created at ./{folder_name}/index.ipynb")

if __name__ == "__main__":
    cli()
