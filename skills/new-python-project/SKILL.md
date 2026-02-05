---
name: new-python-project
description: "Initialize new Python apps, packages, or libraries using UV with Python >=3.14. Use when creating a package (`uv init --package`), app (`uv init <name>`), or library (`uv init --lib`). Ensures project structure, `pyproject.toml` template, ruff + pytest via `uvx`, and git repo creation in /Users/wgu/Documents/PyCharm Projects."
---

# New Python Project (UV) 🚀

## Overview

This skill initializes a new Python project as either a *package* or *library* using UV (https://docs.astral.sh/uv/). If not specified, make it a package. Use this skill when you want a consistent, opinionated starter that:

- Uses Python >=3.14 (written as `requires-python = ">=3.14"`) ✅
- Always runs all commands through `uv` / `uvx` (no direct `pip`/`python`/`ruff`/`pytest` calls) 🔧
- Enforces `ruff` for linting/formatting and `pytest` for tests via `uvx` 💡
- Creates a Git repository rooted at `/Users/wgu/Documents/PyCharm Projects/<project-name>` (initial commit included) ✅

## When to use this skill

- Creating a new package: `uv init --package <name>`
- Creating a new app: `uv init <name>`
- Creating a new library (typed distribution): `uv init --lib <name>`

The helper script `scripts/init_project.py` in this skill automates the `uv` call, patches `pyproject.toml` to the project's canonical template, creates `.python-version`, initializes Git, and creates `py.typed` for libraries.

## Project Templates

App/Package structure (package example):

```
example-pkg
├── .python-version
├── README.md
├── pyproject.toml
└── src
│   └── example_pkg
│       └── py.typed
│       └── __init__.py
├── tests
```

Library structure (typed library example):

```
example-lib
├── .python-version
├── README.md
├── pyproject.toml
└── src
│   └── example_lib
│       └── py.typed
│       └── __init__.py
├── tests
```

## Canonical pyproject.toml (template)

Replace `example-pkg` with your project name and `example_pkg` with the importable package name (hyphens -> underscores):

```
[project]
name = "example-pkg"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "Jared Howland", email = "example-pkg@jaredhowland.com" }
]
requires-python = ">=3.14"
dependencies = []

[project.scripts]
example-pkg = "example_pkg:main"

[build-system]
requires = ["uv_build>=0.9.30,<0.10.0"]
build-backend = "uv_build"
```

Notes:
- All projects should include a `py.typed` file inside the package directory so type checkers treat them as typed.
- `requires-python` must be `">=3.14"` per organizational standard.

## Commands (always via UV)

- Initialize (example package):

  uv init --package example-pkg

- Lint / format with `ruff` via UV: ⚠️ run these through `uvx`

  `uvx ruff format .``
  `uvx ruff check --fix .``

- Run type checkers with `mypy` via UV:

  `uvx mypy .``

- Run tests (pytest) via UV:

  `uvx pytest -q`

## Helper script: `scripts/init_project.py`

This skill includes `scripts/init_project.py`, a small CLI wrapper that:

- Runs `uv init` with the right flags
- Writes `.python-version` (default `3.14`)
- Overwrites `pyproject.toml` with the canonical template shown above
- Creates `py.typed` for `--lib` projects
- Initializes a Git repository in `/Users/wgu/Documents/PyCharm Projects/<name>` and makes an initial commit

Usage examples:

- Create a package:
  `python scripts/init_project.py --type package --name example-pkg --path /Users/wgu/Documents/PyCharm Projects`

- Create a library:
  `python scripts/init_project.py --type lib --name example-lib`

## Safety & Conventions

- All files created by this skill are small, deterministic, and intended as a starting point.
- Use `uvx ruff format .` and `uvx ruff check --fix .` immediately after initialization to ensure consistent formatting.
- Do not embed long boilerplate or copyrighted content. Keep README short and editable.

## Troubleshooting

- If `uv` is not installed, the helper script will exit with a clear message instructing to install `uv` first.
- If the target path exists and is non-empty, the script will refuse to overwrite unless the `--force` flag is used (use cautiously).

## Implementation notes for maintainers

- The script intentionally writes a minimal canonical `pyproject.toml` and will replace whatever `uv init` produced. This enforces the organization's project template (Python version, uv_build backend, empty deps, and a single default script entry).
- Tests for this skill should be included.

---

*Skill created to standardize new Python project creation using UV and to reduce manual setup steps.*
