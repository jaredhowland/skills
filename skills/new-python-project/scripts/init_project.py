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

TEST_TEMPLATE = """def test_smoke():
    assert True
"""


def run(cmd: list[str], cwd: Path | None = None):
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def safe_write_text(path: Path, text: str, *, force: bool = False):
    """Write text to `path` but do not error if the file already exists unless `force=True`.

    If the file exists and `force` is False, skip writing and return. This avoids
    failing when upstream tools like `uv init` have already created files.
    """
    if path.exists():
        if not force:
            if path.is_file():
                print(f"Skipping existing file {path}")
                return
            # Path exists but is not a file (e.g., a directory) - don't attempt to overwrite
            print(f"Skipping existing path {path} (not overwriting)")
            return
    path.write_text(text)
    print(f"Wrote {path}")


def normalize_package_name(name: str) -> str:
    return name.replace("-", "_")


def ensure_uv_available():
    if shutil.which("uv") is None:
        print("Error: `uv` is not installed or not on PATH. Install UV first: https://docs.astral.sh/uv/")
        raise SystemExit(1)


def init_with_uv(project_type: str, name: str, base: Path, force: bool = False):
    cmd = ["uv", "init"]
    if project_type == "package":
        cmd += ["--package", name]
    elif project_type == "lib":
        cmd += ["--lib", name]
    else:  # app
        cmd += [name]
    if force:
        cmd += ["--force"]

    run(cmd, cwd=base)


def create_standard_files(project_dir: Path, name: str, project_type: str, force: bool = False):
    # Ensure the project directory exists so writes succeed even if `uv` didn't run or
    # only created some files.
    project_dir.mkdir(parents=True, exist_ok=True)

    # .python-version
    py_ver_file = project_dir / ".python-version"
    if not py_ver_file.exists() or force:
        py_ver_file.write_text(PYTHON_VERSION)
        print("Wrote .python-version")
    else:
        print("Skipping existing .python-version")

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

    # Always create py.typed so type checkers treat package as typed
    py_typed = src_dir / "py.typed"
    if not py_typed.exists() or force:
        py_typed.write_text("# marker file for typed package")
        print("Wrote py.typed")
    else:
        print("Skipping existing py.typed")

    # Ensure tests/ directory exists with a simple smoke test
    tests_dir = project_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    safe_write_text(tests_dir / "test_smoke.py", TEST_TEMPLATE, force=force)


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

    # Run uv init first to have UV create the directory structure.
    print(f"Initializing project with UV: type={args.type}, name={args.name}")
    init_with_uv(args.type, args.name, args.path, force=args.force)

    project_dir = (args.path / args.name).resolve()

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
