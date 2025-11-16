# AI experiments blog

To install dependencies

```
uv sync
```

To run the blog while in development
```quarto preview ai-experiments/```

Create a site e.g. in github actions
```quarto publish```

## Hiding cells
To hide a cell

```
#| echo: false
#| output: false
```

To hide the code in a code-fold use:

```
#| code-fold: true
```