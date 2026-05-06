#!/usr/bin/env python3
"""Produce native bundles via PyInstaller using ``packaging/alignai.spec``."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path


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
    """Create NSIS installer (Windows only)."""
    import platform

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

    arch = "arm64" if platform.processor() == "ARM64" else "x64"

    # DEBUG: Show platform and architecture info
    print(f"🔍 DEBUG: Platform processor: {platform.processor()}")
    print(f"🔍 DEBUG: Detected architecture: {arch}")
    print(f"🔍 DEBUG: Version: {version}")
    print(f"🔍 DEBUG: Script location: {here}")
    print(f"🔍 DEBUG: Output directory: {output_dir}")

    # For now, create a simple ZIP as placeholder
    # In production, would use NSIS builder
    dist_dir = here / "dist" / "alignai"

    # DEBUG: Check dist directory
    print(f"🔍 DEBUG: Checking dist directory: {dist_dir}")
    print(f"🔍 DEBUG: dist_dir exists: {dist_dir.exists()}")

    if dist_dir.exists():
        # DEBUG: List directory contents
        print(f"🔍 DEBUG: Contents of {dist_dir}:")
        try:
            all_items = list(dist_dir.rglob("*"))
            print(f"🔍 DEBUG: Total items found: {len(all_items)}")
            file_items = [f for f in all_items if f.is_file()]
            print(f"🔍 DEBUG: Total files found: {len(file_items)}")
            if len(file_items) <= 20:
                for item in sorted(file_items):
                    print(f"  - {item.relative_to(dist_dir)}")
            else:
                for item in sorted(file_items)[:20]:
                    print(f"  - {item.relative_to(dist_dir)}")
                print(f"  ... and {len(file_items) - 20} more files")
        except Exception as e:
            print(f"🔍 DEBUG: Error listing directory: {e}")

        zip_path = output_dir / f"AlignAI-{version}-{arch}.zip"
        print(f"🔍 DEBUG: Creating ZIP at: {zip_path}")

        try:
            # Create ZIP manually with zipfile for cross-platform compatibility
            file_count = 0
            with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in dist_dir.rglob("*"):
                    if file_path.is_file():
                        # Create archive name relative to dist_dir parent
                        # (includes 'alignai' folder)
                        arcname = Path("alignai") / file_path.relative_to(dist_dir)
                        try:
                            zf.write(str(file_path), str(arcname))
                            file_count += 1
                        except Exception as e:
                            print(f"🔍 DEBUG: Error adding file {file_path}: {e}")
            print(f"✅ Created ZIP (NSIS placeholder): {zip_path}")
            print(f"🔍 DEBUG: Added {file_count} files to ZIP")
        except Exception as e:
            print(f"❌ ERROR creating ZIP: {e}")
            import traceback

            traceback.print_exc()
            raise
    else:
        print("⚠️  NSIS: PyInstaller output not found at expected location")
        print(f"🔍 DEBUG: Expected directory: {dist_dir}")
        # Check if parent directory exists
        parent = dist_dir.parent
        print(f"🔍 DEBUG: Parent directory exists: {parent.exists()}")
        if parent.exists():
            print(f"🔍 DEBUG: Contents of {parent}:")
            try:
                for item in parent.iterdir():
                    print(f"  - {item.name}")
            except Exception as e:
                print(f"🔍 DEBUG: Error listing parent: {e}")


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default="pyinstaller",
        choices=["pyinstaller", "dmg", "nsis", "appimage"],
        help="Build target: pyinstaller (app bundle only), dmg (macOS), "
        "nsis (Windows), appimage (Linux)",
    )
    args = parser.parse_args()

    # Always build PyInstaller app bundle first
    print("🔨 Building PyInstaller app bundle...")
    app_bundle = _build_pyinstaller()
    print(f"✅ App bundle created: {app_bundle}")

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
    main()
