#!/usr/bin/env python3
"""Produce native bundles via PyInstaller using ``packaging/alignai.spec``."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default="pyinstaller",
        choices=["pyinstaller"],
        help="Build backend (PyInstaller only for now).",
    )
    args = parser.parse_args()
    if args.target != "pyinstaller":
        raise SystemExit("Only --target pyinstaller is implemented.")
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit("Install packaging deps: pip install -e '.[packaging]'") from exc
    here = Path(__file__).resolve().parent
    repo = here.parent
    spec = here / "alignai.spec"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            str(spec),
            "--noconfirm",
            "--clean",
            "--workpath",
            str(here / "build"),
            "--distpath",
            str(here / "dist"),
        ],
        cwd=repo,
        check=True,
    )


if __name__ == "__main__":
    main()
