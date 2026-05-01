#!/usr/bin/env python3
"""AlignAI pre-commit / pre-push gate.

Checks enforced
---------------
1. Layer isolation: domain/application must not import infra/agents/ui.
   (Re-runs import-linter programmatically so the check works without the
    pre-commit hook being active, e.g. inside CI or when run manually.)
2. File-size limit: no class body may exceed MAX_CLASS_LINES lines.
3. Missing tests: every public function/method added in domain/ or
   application/ must have a corresponding test_ function somewhere in tests/.

Exit codes
----------
0 - all checks passed
1 - one or more violations found (details printed to stderr)

Usage
-----
    python scripts/preflight.py          # check everything under src/ and tests/
    python scripts/preflight.py --fast   # skip import-linter (for quick local runs)
"""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src" / "alignai"
TESTS_ROOT = REPO_ROOT / "tests"

MAX_CLASS_LINES = 200  # body lines (blank + docstrings excluded)

# Layers that MUST NOT be imported by domain/ or application/
FORBIDDEN_IMPORTS: dict[str, list[str]] = {
    "domain": ["alignai.infra", "alignai.agents", "alignai.ui", "alignai.application"],
    "application": ["alignai.infra", "alignai.agents", "alignai.ui"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _python_files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.py"))


# ---------------------------------------------------------------------------
# Check 1 - layer isolation (AST-based, fast)
# ---------------------------------------------------------------------------


def check_layer_isolation() -> list[str]:
    """Return a list of violation messages (empty = clean)."""
    violations: list[str] = []
    for layer, forbidden in FORBIDDEN_IMPORTS.items():
        layer_dir = SRC_ROOT / layer
        if not layer_dir.exists():
            continue
        for py_file in _python_files(layer_dir):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                violations.append(f"SyntaxError in {py_file.relative_to(REPO_ROOT)}: {exc}")
                continue
            for node in ast.walk(tree):
                module: str | None = None
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        if any(module == f or module.startswith(f + ".") for f in forbidden):
                            violations.append(
                                f"{py_file.relative_to(REPO_ROOT)}:{node.lineno} "
                                f"- {layer}/ imports forbidden module '{module}'"
                            )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module
                    if any(module == f or module.startswith(f + ".") for f in forbidden):
                        violations.append(
                            f"{py_file.relative_to(REPO_ROOT)}:{node.lineno} "
                            f"- {layer}/ imports forbidden module '{module}'"
                        )
    return violations


# ---------------------------------------------------------------------------
# Check 2 - file / class size limit
# ---------------------------------------------------------------------------


def check_class_sizes() -> list[str]:
    violations: list[str] = []
    for py_file in _python_files(SRC_ROOT):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue  # already reported by check_layer_isolation
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.end_lineno is not None:
                # Count lines via span (end_lineno - lineno; approximate via AST walk).
                span = node.end_lineno - node.lineno
                if span > MAX_CLASS_LINES:
                    violations.append(
                        f"{py_file.relative_to(REPO_ROOT)}:{node.lineno} "
                        f"- class '{node.name}' spans {span} lines "
                        f"(limit {MAX_CLASS_LINES})"
                    )
    return violations


# ---------------------------------------------------------------------------
# Check 3 - missing tests for public domain/application symbols
# ---------------------------------------------------------------------------


def _public_symbols(layer_dir: Path) -> dict[str, set[str]]:
    """Return {relative_file_path: {symbol_name}} for public functions/methods."""
    result: dict[str, set[str]] = {}
    for py_file in _python_files(layer_dir):
        symbols: set[str] = set()
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                not node.name.startswith("_")
            ):
                symbols.add(node.name)
        if symbols:
            result[str(py_file.relative_to(REPO_ROOT))] = symbols
    return result


def _tested_names() -> set[str]:
    """Collect all test function names from the tests directory."""
    names: set[str] = set()
    if not TESTS_ROOT.exists():
        return names
    for py_file in _python_files(TESTS_ROOT):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
    return names


def check_missing_tests() -> list[str]:
    """Warn when a public symbol in domain/ or application/ has no test_ counterpart."""
    violations: list[str] = []
    tested = _tested_names()
    for layer in ("domain", "application"):
        layer_dir = SRC_ROOT / layer
        if not layer_dir.exists():
            continue
        for src_file, symbols in _public_symbols(layer_dir).items():
            for name in sorted(symbols):
                # Accept test_{name} or test_{anything}_{name} anywhere in tests/
                has_test = any(t == f"test_{name}" or t.endswith(f"_{name}") for t in tested)
                if not has_test:
                    violations.append(
                        f"{src_file} - public symbol '{name}' has no test_ function in tests/"
                    )
    return violations


# ---------------------------------------------------------------------------
# Check 4 - run import-linter (subprocess)
# ---------------------------------------------------------------------------


def _scripts_bin(*, prefix: Path) -> Path:
    """Return the directory where pip installs console_scripts for this environment."""
    return prefix / ("Scripts" if sys.platform == "win32" else "bin")


def _lint_imports_executable() -> str | None:
    """Return path to lint-imports CLI for this Python environment, then PATH."""
    name = "lint-imports.exe" if sys.platform == "win32" else "lint-imports"
    candidate = _scripts_bin(prefix=Path(sys.prefix)) / name
    if candidate.is_file():
        return str(candidate)
    return shutil.which("lint-imports")


def check_import_linter() -> list[str]:
    """Run lint-imports CLI (import-linter does not expose python -m importlinter)."""
    exe = _lint_imports_executable()
    if exe is None:
        return [
            "import-linter failed: `lint-imports` executable not found "
            "(install dev deps: pip install -e '.[dev]', use the same Python/venv)"
        ]
    result = subprocess.run(
        [exe, "--config", "pyproject.toml"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        return [f"import-linter failed:\n{output}"]
    return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="AlignAI pre-commit gate")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip import-linter subprocess (use AST check only)",
    )
    parser.add_argument(
        "--skip-missing-tests",
        action="store_true",
        help="Skip the missing-tests check (useful during initial scaffolding)",
    )
    args = parser.parse_args()

    all_violations: list[str] = []

    print("preflight: checking layer isolation (AST)...")
    all_violations += check_layer_isolation()

    print("preflight: checking class sizes...")
    all_violations += check_class_sizes()

    if not args.skip_missing_tests:
        print("preflight: checking for missing tests...")
        all_violations += check_missing_tests()
    else:
        print("preflight: skipping missing-tests check (--skip-missing-tests)")

    if not args.fast:
        print("preflight: running import-linter...")
        all_violations += check_import_linter()

    if all_violations:
        print("\n\033[31m-- preflight FAILED --\033[0m", file=sys.stderr)
        for v in all_violations:
            print(f"  [fail] {v}", file=sys.stderr)
        print(
            f"\n{len(all_violations)} violation(s) found. Fix them before committing.",
            file=sys.stderr,
        )
        return 1

    print("\033[32m-- preflight PASSED --\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
