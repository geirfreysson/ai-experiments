# /// script
# dependencies = [
#   "requests",
#   "ollama",
#   "click",
#   "nbformat",
#   "bs4"
# ]
# ///

import requests
import nbformat
import datetime
import ollama
import click
from bs4 import BeautifulSoup

# Function to fetch website content
def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Attempt to find main content from common semantic tags
        main_content = soup.find("article")  # Most blogs use <article> for posts
        if not main_content:
            main_content = soup.find("main")  # Try <main> if <article> isn't present
        if not main_content:
            main_content = soup.find("div", {"class": "content"})  # Generic fallback
        
        # Extract text content
        if main_content:
            return main_content.get_text(separator="\n").strip()
        else:
            # Fallback to all paragraphs if no main content is found
            paragraphs = soup.find_all("p")
            return "\n\n".join(p.get_text() for p in paragraphs).strip()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching website: {e}")
    
# Function to summarize content using Ollama
def summarize_content(content, model="dolphin-mistral"):
    try:
        ollama_prompt = f"Summarize the following website content in one short paragraph:\n\n{content}"
        summary = ollama.generate(model=model, prompt=ollama_prompt)
        return summary
    except Exception as e:
        return f"Error summarizing content: {e}"

# Function to create a Jupyter notebook with Quarto frontmatter
def create_notebook(summary, url):
    # Quarto frontmatter
    frontmatter = f"""
---
title: "Summary of {url}"
author: "Generated by Python Script"
date: {datetime.date.today().isoformat()}
categories: [summary, automation]
---
"""
    
    # Create notebook cells
    cells = [
        nbformat.v4.new_raw_cell(frontmatter),
        nbformat.v4.new_markdown_cell(f"# Summary of {url}"),
        nbformat.v4.new_markdown_cell("# The following is an outline of the website content."),
        nbformat.v4.new_markdown_cell(summary)
    ]

    # Create notebook structure
    nb = nbformat.v4.new_notebook()
    nb.cells = cells

    # Save the notebook
    filename = f"summary_{datetime.date.today().isoformat()}.ipynb"
    with open(filename, "w") as f:
        nbformat.write(nb, f)

    return filename

# CLI using Click
@click.command()
@click.argument("url")
@click.option("--model", default="dolphin-mistral", help="Specify the Ollama model to use.")
def main(url, model):
    """
    Fetch a website content from the given URL, summarize it using Ollama, 
    and create a Jupyter notebook with Quarto frontmatter.
    """
    click.echo(f"Fetching content from {url}...")
    content = fetch_website_content(url)
        
    click.echo("Summarizing content...")
    summary = summarize_content(content, model=model)
    
    if "Error" in summary:
        click.echo(summary)
        return
    
    click.echo("Generating Jupyter Notebook...")
    notebook_path = create_notebook(summary.response, url)
    click.echo(f"Notebook created: {notebook_path}")

if __name__ == "__main__":
    main()