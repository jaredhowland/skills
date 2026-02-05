#!/usr/bin/env python3
"""Simple helper to initialize new Python projects using UV.

This script is intentionally small and deterministic so it can be used by the
skill to create a standard project layout.

Usage examples:
    python init_project.py --type package --name example-pkg
    python init_project.py --type lib --name example-lib
    python init_project.py --type app --name example-app --path /Users/wgu/Documents/PyCharm Projects

Notes:
- All commands are run through `uv`/`uvx` where appropriate
- The script will refuse to operate on a non-empty target directory unless --force is passed
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
import sys

DEFAULT_BASE = Path("/Users/wgu/Documents/PyCharm Projects")
PYTHON_VERSION = "3.14"
UV_BUILD_REQUIRE = "uv_build>=0.9.30,<0.10.0"

PYPROJECT_TEMPLATE = """[project]
name = "{proj_name}"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[project.scripts]
{console_name} = "{package_name}:main"

[build-system]
requires = ["{uv_build}"]
build-backend = "uv_build"
"""

README_TEMPLATE = """# {proj_name}

Short description for {proj_name}.
"""

INIT_PY_TEMPLATE = """def main():
    # Entry point placeholder for {proj_name}
    print("Hello from {proj_name}")
"""


def run(cmd: list[str], cwd: Path | None = None):
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def safe_write_text(path: Path, text: str, *, force: bool = False):
    if path.exists() and path.is_file() and not force:
        print(f"Refusing to overwrite {path} (use --force to override)")
        raise SystemExit(1)
    path.write_text(text)
    print(f"Wrote {path}")


def normalize_package_name(name: str) -> str:
    return name.replace("-", "_")


def ensure_uv_available():
    if shutil.which("uv") is None:
        print("Error: `uv` is not installed or not on PATH. Install UV first: https://docs.astral.sh/uv/")
        raise SystemExit(1)


def init_with_uv(project_type: str, name: str, base: Path):
    cmd = ["uv", "init"]
    if project_type == "package":
        cmd += ["--package", name]
    elif project_type == "lib":
        cmd += ["--lib", name]
    else:  # app
        cmd += [name]

    run(cmd, cwd=base)


def create_standard_files(project_dir: Path, name: str, project_type: str, force: bool = False):
    # .python-version
    (project_dir / ".python-version").write_text(PYTHON_VERSION)
    print("Wrote .python-version")

    # README
    safe_write_text(project_dir / "README.md", README_TEMPLATE.format(proj_name=name), force=force)

    # Overwrite pyproject.toml with canonical template
    package_name = normalize_package_name(name)
    console_name = name
    pyproject = PYPROJECT_TEMPLATE.format(
        proj_name=name, package_name=package_name, console_name=console_name, uv_build=UV_BUILD_REQUIRE
    )
    safe_write_text(project_dir / "pyproject.toml", pyproject, force=force)

    # Ensure src/<package>/__init__.py exists
    src_dir = project_dir / "src" / package_name
    src_dir.mkdir(parents=True, exist_ok=True)
    safe_write_text(src_dir / "__init__.py", INIT_PY_TEMPLATE.format(proj_name=name), force=force)

    # For libraries, create py.typed
    if project_type == "lib":
        (src_dir / "py.typed").write_text("# marker file for typed package")
        print("Wrote py.typed")


def init_git(project_dir: Path):
    if (project_dir / ".git").exists():
        print("Git already initialized; skipping git init")
        return
    run(["git", "init"], cwd=project_dir)
    run(["git", "add", "-A"], cwd=project_dir)
    run(["git", "commit", "-m", "chore: initial commit"], cwd=project_dir)
    print("Initialized git and created initial commit")


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize a new Python project using UV and apply canonical project template")
    parser.add_argument("--type", choices=("app", "package", "lib"), default="package")
    parser.add_argument("--name", required=True, help="Project name (hyphenated). e.g., example-pkg")
    parser.add_argument("--path", type=Path, default=DEFAULT_BASE, help=f"Base path to create the project (default: {DEFAULT_BASE})")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files where safe")
    return parser.parse_args()


def main():
    args = parse_args()

    ensure_uv_available()

    project_dir = (args.path / args.name).resolve()
    if project_dir.exists() and any(project_dir.iterdir()) and not args.force:
        print(f"Error: target directory {project_dir} already exists and is not empty. Use --force to override.")
        raise SystemExit(1)

    # Run uv init
    print(f"Initializing project with UV: type={args.type}, name={args.name}")
    if (project_dir / "pyproject.toml").exists():
        print("pyproject.toml already exists; skipping uv init")
    else:
        init_with_uv(args.type, args.name, args.path)

    # Create canonical files and structure
    create_standard_files(project_dir, args.name, args.type, force=args.force)

    # Init git
    init_git(project_dir)

    print("\nDone. Next steps:")
    print("  cd", project_dir)
    print("  uvx ruff format .")
    print("  uvx ruff check --fix .")
    print("  uvx pytest -q")


if __name__ == "__main__":
    main()
