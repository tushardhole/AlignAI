#!/usr/bin/env python3
"""Sign and notarize macOS artifacts (DMG, app bundle)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def sign_dmg(dmg_path: Path) -> None:
    """Sign DMG using codesign (requires Apple Developer ID)."""
    developer_id = os.getenv("APPLE_DEVELOPER_ID")
    if not developer_id:
        print("⚠️  APPLE_DEVELOPER_ID not set, skipping code signing")
        return

    print(f"🔐 Signing DMG: {dmg_path}")
    subprocess.run(
        [
            "codesign",
            "-s",
            developer_id,
            "-v",
            str(dmg_path),
        ],
        check=True,
    )
    print(f"✅ Signed: {dmg_path}")


def notarize_dmg(dmg_path: Path) -> None:
    """Notarize DMG with Apple (requires credentials)."""
    apple_id = os.getenv("APPLE_ID")
    apple_team_id = os.getenv("APPLE_TEAM_ID")
    apple_app_password = os.getenv("APPLE_APP_PASSWORD")

    if not all([apple_id, apple_team_id, apple_app_password]):
        print("⚠️  Apple notarization credentials not set, skipping notarization")
        return

    print(f"🔔 Notarizing DMG: {dmg_path}")

    # Submit for notarization
    result = subprocess.run(
        [
            "xcrun",
            "notarytool",
            "submit",
            str(dmg_path),
            "--apple-id",
            apple_id,
            "--team-id",
            apple_team_id,
            "--password",
            apple_app_password,
            "--wait",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✅ Notarization successful: {dmg_path}")
    else:
        print(f"❌ Notarization failed: {result.stderr}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, help="Path to dist-installers/ directory")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts)
    if not artifacts_dir.exists():
        print(f"❌ Artifacts directory not found: {artifacts_dir}")
        sys.exit(1)

    # Find all DMG files
    dmg_files = list(artifacts_dir.glob("*.dmg"))
    if not dmg_files:
        print("⚠️  No DMG files found in artifacts directory")
        return

    print(f"Found {len(dmg_files)} DMG file(s) to sign/notarize")

    for dmg_path in dmg_files:
        try:
            sign_dmg(dmg_path)
            notarize_dmg(dmg_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error processing {dmg_path}: {e}")
            # Continue with other files
            continue

    print("✅ All signing/notarization complete")


if __name__ == "__main__":
    main()
