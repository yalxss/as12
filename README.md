# as12

Contribution grid design utility for GitHub profiles.

## Overview

A command-line script to schedule and plot pixel art, typography, or custom patterns onto the annual contribution graph.

## Requirements

- Python 3.11+
- Git

## Quick Start

### Terminal preview

```bash
python cli.py --text "DEV" --preview
python cli.py --pattern heart --preview
```

### Commit generation

```bash
python cli.py --text "CODE" --year 2026 --generate
```

## Flags

- `--text <string>`: Text to render centered on the 52x7 matrix.
- `--pattern <name>`: Preconfigured pattern (heart, arcade, wave).
- `--file <path>`: Custom 7-row ASCII input file.
- `--year <int>`: Target year for commit scheduling (default: 2026).
- `--rolling`: Rolling 52-week window from the current week.
- `--preview`: Display colored terminal map without creating commits.
- `--generate`: Execute commit generation in the local repository.
- `--author-name <string>`: Commit author name.
- `--author-email <string>`: Commit author email address.
- `--tz <string>`: Timezone offset string (e.g. +0300).

## Configuration

Weights and author defaults can be modified in `config.json`.
