# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run the application: `python app.py`
- Install dependencies: `pip install -e .` 
- Format code: `black .`
- Lint code: `flake8 .`
- Check types: `mypy .`

## Code Style Guidelines

- Python version: >=3.12
- Use type hints for all function parameters and return values
- Format imports: standard library first, then third-party, then local
- Naming: snake_case for variables/functions, PascalCase for classes
- Line length: 88 characters (Black default)
- Docstrings: Use Google style for all functions and classes
- Error handling: Use explicit try/except blocks with specific exceptions
- Flask routes should have clear path names and explicit HTTP methods
- When using Altair, explicitly specify encoding types (quantitative, nominal, etc.)
- React to type errors early and explicitly