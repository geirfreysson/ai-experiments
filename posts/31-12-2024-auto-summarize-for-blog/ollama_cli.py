# /// script
# dependencies = [
#   "requests",
#   "ollama",
#   "click",
#   "nbformat",
#   "bs4",
#   "dynaconf"
# ]
# ///

import click
import requests
from bs4 import BeautifulSoup
import ollama
from config import settings

# Function to fetch main content from a website
def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Attempt to find the main content
        main_content = soup.find("article") or soup.find("main") or soup.find("div", {"class": "content"})
        if main_content:
            return main_content.get_text(separator="\n").strip()
        else:
            paragraphs = soup.find_all("p")
            return "\n\n".join(p.get_text() for p in paragraphs).strip()
    except requests.exceptions.RequestException as e:
        return f"Error fetching website: {e}"


# Function to interact with Ollama
def chat_with_ollama(prompt, model):
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response
    except Exception as e:
        return f"Error interacting with Ollama: {e}"


# CLI using Click
@click.group()
def cli():
    """A command-line tool to interact with Ollama."""
    pass


# Command to send a custom prompt to Ollama
@cli.command()
@click.argument("prompt")
@click.option("--model", default="dolphin-mistral", help="Specify the Ollama model to use.")
def prompt(prompt, model):
    """Send a custom prompt to Ollama."""
    click.echo(f"Sending prompt to Ollama with model '{model}'...")
    response = chat_with_ollama(prompt, model)
    click.echo(response)


# Command to summarize website content using Ollama
@cli.command()
@click.argument("url")
@click.option("--model", default="dolphin-mistral", help="Specify the Ollama model to use.")
def summarize(url, model):
    """Fetch a website and summarize its content using Ollama."""
    click.echo(f"Fetching content from {url}...")
    content = fetch_website_content(url)
    if "Error" in content:
        click.echo(content)
        return

    click.echo("Summarizing content...")
    summary = chat_with_ollama(f"Summarize the following content:\n\n{content}", model)
    click.echo(summary)


# Command to test predefined prompts
@cli.command()
@click.option("--model", default="dolphin-mistral", help="Specify the Ollama model to use.")
def test(model):
    """Run predefined prompts to test Ollama."""
    test_prompts = [
        "What is the capital of France?",
        "Explain the concept of quantum computing in simple terms.",
        "Provide three tips for staying productive while working remotely."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        click.echo(f"\nTest Prompt {i}: {prompt}")
        response = chat_with_ollama(prompt, model)
        click.echo(response)


if __name__ == "__main__":
    import pdb; pdb.set_trace()
    cli()
