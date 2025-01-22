#!/bin/bash

# Check if a URL was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

URL=$1  # Assign the first argument to a variable

uv run shot-scraper "$URL" \
-h 418 -w 800 --javascript "
document.querySelector('h1.title').style.fontSize='3em';
document.querySelector('.navbar-toggler-icon').style.display = 'none';
document.querySelectorAll('section').forEach(el => el.style.display = 'none');
document.querySelector('.navbar-brand-logo img').style.height='120px';
document.querySelector('.quarto-title').style.marginTop='40px';
"
