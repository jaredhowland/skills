---
agent: 'agent'
model: GPT-5 mini
description: 'Start a new Python app, package or library'
---

# New Python Project

Create a new Python project (app, package, or library) using UV.

## Instructions

**If the project type is not specified, default to `package`.**

All projects are created inside `/Users/wgu/Documents/PyCharm Projects`.

### 1. Initialize with UV

Use Python `>=3.14`. Choose the correct command based on project type:

| Type    | Command                           |
| ------- | --------------------------------- |
| App     | `uv init {PROJECT_NAME}`         |
| Package | `uv init --package {PROJECT_NAME}` |
| Library | `uv init --lib {PROJECT_NAME}`   |

Run the `uv init` command from `/Users/wgu/Documents/PyCharm Projects`.

### 2. Project Structure

After `uv init`, ensure the project matches the expected layout.

**App or Package:**

```
{project-name}
├── .python-version
├── README.md
├── pyproject.toml
└── src
    └── {project_name}
        └── __init__.py
```

**Library:**

```
{project-name}
├── .python-version
├── README.md
├── pyproject.toml
└── src
    └── {project_name}
        ├── py.typed
        └── __init__.py
```

`{project-name}` uses hyphens (e.g., `example-pkg`). `{project_name}` uses underscores (e.g., `example_pkg`).

### 3. `pyproject.toml`

Ensure `pyproject.toml` contains exactly this structure (adapting names):

```toml
[project]
name = "{project-name}"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[project.scripts]
{project-name} = "{project_name}:main"

[build-system]
requires = ["uv_build>=0.9.30,<0.10.0"]
build-backend = "uv_build"
```

If `uv init` generates a different `pyproject.toml`, edit it to match the above.

### 4. Tooling

All commands run through UV. Never install tools globally — use `uvx`.

- **Linting:** `uvx ruff check --fix .`
- **Formatting:** `uvx ruff format .`
- **Testing:** `uvx pytest -q`

Run ruff check, ruff format, and pytest after project creation to verify everything works.

### 5. Git Repository

Initialize a git repository in the new project directory:

```sh
cd "/Users/wgu/Documents/PyCharm Projects/{project-name}"
git init
git add .
git commit -m "Initial commit"
```

### 6. Summary

After completing all steps, confirm:
- Project directory created at `/Users/wgu/Documents/PyCharm Projects/{project-name}`
- `pyproject.toml` matches the required format
- Ruff lint + format pass
- Pytest runs successfully
- Git repo initialized with initial commit
