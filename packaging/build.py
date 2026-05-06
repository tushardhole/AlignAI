#!/usr/bin/env python3
"""Produce native bundles via PyInstaller using ``packaging/alignai.spec``."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

# Emergency early-stage error detection
print("🔍 Starting build.py", file=sys.stderr, flush=True)
print(f"🔍 Python version: {sys.version}", file=sys.stderr, flush=True)
print(f"🔍 Platform: {sys.platform}", file=sys.stderr, flush=True)


def _build_pyinstaller() -> Path:
    """Build app bundle using PyInstaller."""
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
    return here / "dist" / "alignai.app"


def _build_dmg(app_bundle: Path) -> None:
    """Create DMG from app bundle (macOS only)."""
    here = Path(__file__).resolve().parent
    output_dir = here.parent / "dist-installers"
    output_dir.mkdir(exist_ok=True)

    # Get version from Git tag or use 0.1.0
    try:
        version = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=here.parent,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        if version.startswith("v"):
            version = version[1:]
    except Exception:
        version = "0.1.0"

    # Determine architecture
    import platform

    arch = "arm64" if platform.processor() == "arm" else "x86_64"

    dmg_path = output_dir / f"AlignAI-{version}-{arch}.dmg"

    # Create DMG using hdiutil
    subprocess.run(
        [
            "hdiutil",
            "create",
            "-volname",
            "AlignAI",
            "-srcfolder",
            str(app_bundle),
            "-ov",
            "-format",
            "UDZO",
            str(dmg_path),
        ],
        check=True,
    )
    print(f"✅ Created DMG: {dmg_path}")


def _build_nsis() -> None:
    """Create Windows installer (NSIS placeholder using ZIP)."""
    import platform

    here = Path(__file__).resolve().parent
    output_dir = here.parent / "dist-installers"
    output_dir.mkdir(exist_ok=True)

    print("🔍 DEBUG: _build_nsis() called")

    # Get version
    try:
        version = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=here.parent,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        if version.startswith("v"):
            version = version[1:]
    except Exception:
        version = "0.1.0"

    processor = platform.processor().upper()
    arch = "arm64" if processor in ("ARM64", "ARM") else "x64"

    print(f"🔍 DEBUG: Platform processor: {processor}")
    print(f"🔍 DEBUG: Detected architecture: {arch}")
    print(f"🔍 DEBUG: Version: {version}")

    # Locate PyInstaller output directory
    dist_dir = here / "dist" / "alignai"
    print(f"🔍 DEBUG: Looking for dist directory: {dist_dir}")

    # Try to find alignai directory (may have different name on some platforms)
    if not dist_dir.exists():
        dist_parent = here / "dist"
        if dist_parent.exists():
            # Look for any directory that might be our output
            for item in dist_parent.iterdir():
                if item.is_dir():
                    print(f"🔍 DEBUG: Found directory in dist/: {item.name}")
                    if "alignai" in item.name.lower():
                        dist_dir = item
                        break

    if not dist_dir.exists():
        msg = f"PyInstaller output not found at {dist_dir}"
        print(f"❌ ERROR: {msg}")
        raise FileNotFoundError(msg)

    # Create ZIP file from PyInstaller output
    zip_path = output_dir / f"AlignAI-{version}-{arch}.zip"
    print(f"🔍 DEBUG: Creating ZIP at: {zip_path}")

    try:
        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for file_path in sorted(dist_dir.rglob("*")):
                if file_path.is_file():
                    rel_path = file_path.relative_to(dist_dir)
                    # Use forward slashes for ZIP archives
                    arcname = f"alignai/{rel_path.as_posix()}"
                    zf.write(str(file_path), arcname)
                    file_count += 1
        print(f"✅ Created ZIP: {zip_path} ({file_count} files)")
    except Exception as e:
        print(f"❌ ERROR creating ZIP: {e}")
        import traceback

        traceback.print_exc()
        raise


def _build_appimage() -> None:
    """Create AppImage (Linux only)."""
    here = Path(__file__).resolve().parent
    output_dir = here.parent / "dist-installers"
    output_dir.mkdir(exist_ok=True)

    # Get version
    try:
        version = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=here.parent,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        if version.startswith("v"):
            version = version[1:]
    except Exception:
        version = "0.1.0"

    import platform

    arch = platform.machine()

    # For now, create a TAR.GZ as placeholder
    # In production, would use appimagetool or linuxdeploy
    dist_dir = here / "dist" / "alignai"
    if dist_dir.exists():
        tar_path = output_dir / f"AlignAI-{version}-{arch}.tar.gz"
        subprocess.run(
            ["tar", "-czf", str(tar_path), "-C", str(dist_dir.parent), "alignai"],
            check=True,
        )
        print(f"✅ Created TAR.GZ (AppImage placeholder): {tar_path}")
    else:
        print("⚠️  AppImage: PyInstaller output not found at expected location")


def main() -> None:
    import os
    import sys as sys_module

    # Emergency debug output to stderr to ensure visibility
    print("🔍 DEBUG: main() called", file=sys_module.stderr, flush=True)
    print(f"🔍 DEBUG: sys.argv: {sys_module.argv}", file=sys_module.stderr, flush=True)
    print(f"🔍 DEBUG: cwd: {os.getcwd()}", file=sys_module.stderr, flush=True)
    print(
        f"🔍 DEBUG: PYTHONPATH: {os.environ.get('PYTHONPATH', 'not set')}",
        file=sys_module.stderr,
        flush=True,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default="pyinstaller",
        choices=["pyinstaller", "dmg", "nsis", "appimage"],
        help="Build target: pyinstaller (app bundle only), dmg (macOS), "
        "nsis (Windows), appimage (Linux)",
    )
    args = parser.parse_args()
    print(f"🔍 DEBUG: parsed target: {args.target}", file=sys_module.stderr, flush=True)

    # Always build PyInstaller app bundle first
    print("🔨 Building PyInstaller app bundle...", flush=True)
    app_bundle = _build_pyinstaller()
    print(f"✅ App bundle created: {app_bundle}", flush=True)

    # Then create platform-specific installer
    if args.target == "pyinstaller":
        print("✅ PyInstaller build complete")
    elif args.target == "dmg":
        print("📦 Creating macOS DMG...")
        _build_dmg(app_bundle)
    elif args.target == "nsis":
        print("📦 Creating Windows NSIS installer...")
        _build_nsis()
    elif args.target == "appimage":
        print("📦 Creating Linux AppImage...")
        _build_appimage()


if __name__ == "__main__":
    import logging
    import traceback

    # Set up logging to a file AND stdout
    # Write to dist-installers so it's uploaded as artifact
    dist_installers = Path(__file__).parent.parent / "dist-installers"
    dist_installers.mkdir(exist_ok=True)
    log_path = dist_installers / "build.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )

    try:
        main()
    except Exception as e:
        logging.error(f"Build failed with exception: {e}")
        traceback.print_exc()
        # Also write traceback to file
        with open(log_path, "a") as f:
            f.write("\n=== TRACEBACK ===\n")
            f.write(traceback.format_exc())
        sys.exit(1)
