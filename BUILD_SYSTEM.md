# AlignAI Multi-Platform Build System

## Overview

This document describes the automated build system for creating distributable artifacts for AlignAI across all major platforms and architectures.

## Architecture

### Build Workflow

```
GitHub Push → build-test.yml OR release.yml
    ↓
Python 3.12 Setup + Dependencies
    ↓
PyInstaller (packaging/build.py --target pyinstaller)
    ├── Creates: packaging/dist/alignai.app (macOS bundle)
    ├── Creates: packaging/dist/alignai/ (Windows/Linux folder)
    ↓
Platform-Specific Installer Builder
    ├── macOS: _build_dmg() → dist-installers/*.dmg
    ├── Windows: _build_nsis() → dist-installers/*.zip (placeholder)
    ├── Linux: _build_appimage() → dist-installers/*.tar.gz (placeholder)
    ↓
SHA256 Checksum Generation
    ↓
Artifact Upload (GitHub workflow artifacts or GitHub Release)
    ↓ (release.yml only)
Code Signing & Notarization (macOS)
    ↓ (release.yml only)
GitHub Release Creation with all artifacts
```

## Workflows

### 1. build-test.yml (Manual Testing)

**Trigger**: Manual via GitHub Actions UI
**Purpose**: Test builds on all platforms without creating a GitHub Release

**Builds on**:
- macOS 14 (arm64) → DMG
- macOS 13 (x86_64) → DMG
- Windows Latest (x64) → ZIP
- Ubuntu 22.04 (x86_64) → TAR.GZ

**Output**: Workflow artifacts (7-day retention)

**Usage**:
1. Go to GitHub Actions
2. Select "Build Test (Manual)"
3. Click "Run workflow"
4. Wait for builds to complete
5. Download artifacts from workflow run

### 2. release.yml (Production Release)

**Trigger**: Git tag (v*.*.*)
**Purpose**: Build, sign, and publish all artifacts to GitHub Release

**Builds on**: Same platforms as build-test.yml + arm64 variants
**Output**: GitHub Release with downloadable artifacts

**Additional Steps**:
- Code signing for macOS (requires Apple Developer ID)
- Notarization for macOS (requires Apple ID + Team ID)
- SBOM generation
- SLSA provenance attestation

## Build System Implementation

### packaging/build.py

Enhanced PyInstaller build orchestrator supporting multiple targets:

```bash
# Build app bundle only (all platforms)
python packaging/build.py --target pyinstaller

# Create platform-specific installers
python packaging/build.py --target dmg        # macOS
python packaging/build.py --target nsis       # Windows
python packaging/build.py --target appimage   # Linux
```

**Build Steps**:
1. Verify PyInstaller is installed
2. Run PyInstaller with spec file
3. Generate platform-specific installer from app bundle
4. Output to `dist-installers/` directory

### packaging/signer.py

Handles macOS code signing and notarization:

```bash
python packaging/signer.py --artifacts dist-installers/
```

**Features**:
- Code signing with Apple Developer ID
- Notarization with Apple servers
- Requires environment variables:
  - `APPLE_DEVELOPER_ID`: Signing certificate identifier
  - `APPLE_ID`: Apple ID email
  - `APPLE_TEAM_ID`: Apple Team ID
  - `APPLE_APP_PASSWORD`: App-specific password

## Output Structure

After a successful build, artifacts appear in `dist-installers/`:

```
dist-installers/
├── AlignAI-{version}-arm64.dmg           # macOS (Apple Silicon)
├── AlignAI-{version}-x86_64.dmg          # macOS (Intel)
├── AlignAI-{version}-Setup-x64.zip       # Windows (x64)
├── AlignAI-{version}-Setup-arm64.zip     # Windows (arm64)
├── AlignAI-{version}-x86_64.tar.gz       # Linux (x86_64)
├── AlignAI-{version}-arm64.tar.gz        # Linux (arm64)
├── SHA256SUMS.txt                        # Checksums for all artifacts
└── sbom.spdx.json                        # Software Bill of Materials (release only)
```

## Current Implementation Status

### ✅ Implemented
- PyInstaller integration
- macOS DMG creation (native `hdiutil`)
- Windows ZIP placeholder (ready for NSIS integration)
- Linux TAR.GZ placeholder (ready for AppImage integration)
- macOS code signing & notarization support
- SHA256 checksum generation
- Workflow artifacts/releases

### ⏳ Future Improvements
- Windows: Integrate NSIS installer builder
- Linux: Integrate AppImage builder
- Windows arm64: Test on Windows-11-arm runner
- Linux arm64: Test on Ubuntu-arm runner
- Enhanced icons (.icns for macOS, .ico for Windows)
- License file in installers
- macOS code signing CI/CD integration

## Testing Instructions

### Test Build Workflow

1. **Trigger manual build-test workflow**:
   ```bash
   gh workflow run build-test.yml --ref master
   ```

2. **Monitor progress**:
   ```bash
   gh run list --workflow=build-test.yml --limit 1
   ```

3. **Download artifacts**:
   - Go to GitHub Actions → Build Test run
   - Download artifacts for each platform
   - Verify file names and sizes

### Test Release Workflow

1. **Create test release tag**:
   ```bash
   git tag -a v0.2.0-rc1 -m "Release candidate 1"
   git push origin v0.2.0-rc1
   ```

2. **Monitor workflow**:
   ```bash
   gh run list --workflow=release.yml --limit 1
   ```

3. **Download from GitHub Release**:
   - Go to GitHub Releases
   - Download .dmg, .zip, .tar.gz files
   - Verify checksums: `sha256sum -c SHA256SUMS.txt`

4. **Test installation**:
   - **macOS**: Double-click DMG, drag app to Applications
   - **Windows**: Extract ZIP, run setup
   - **Linux**: Extract TAR.GZ, run binary

## Environment Variables for Code Signing

For release builds with code signing, set these in GitHub Repository Secrets:

- `APPLE_DEVELOPER_ID`: Developer ID certificate name (e.g., "Developer ID Application: Company Name (ABCD123456)")
- `APPLE_ID`: Apple ID email
- `APPLE_TEAM_ID`: Team ID (e.g., "ABC123DEF4")
- `APPLE_APP_PASSWORD`: App-specific password from Apple ID account

## File Structure

```
AlignAI/
├── packaging/
│   ├── build.py              # Main build orchestrator
│   ├── signer.py             # macOS code signing & notarization
│   ├── alignai.spec          # PyInstaller configuration
│   ├── icons/
│   │   ├── icon.png          # Linux icon (512x512)
│   │   └── icon_small.png    # Other sizes
│   ├── build/                # PyInstaller working directory
│   └── dist/                 # PyInstaller output
├── dist-installers/          # Final distributable artifacts
├── .github/workflows/
│   ├── build-test.yml        # Manual test workflow
│   └── release.yml           # Production release workflow
└── BUILD_SYSTEM.md           # This file
```

## Troubleshooting

### Build Fails: "PyInstaller not installed"
```bash
pip install -e ".[packaging]"
```

### macOS DMG creation fails
- Ensure `hdiutil` is available (built-in on macOS)
- Check disk space for temporary files
- Verify app bundle exists at `packaging/dist/alignai.app`

### Windows/Linux placeholder installers need actual builders
Currently outputs ZIP (Windows) and TAR.GZ (Linux) as placeholders.
For production:
- **Windows**: Integrate NSIS builder (requires NSIS on Windows runner)
- **Linux**: Integrate appimagetool (requires appimagetool on Linux runner)

## Version Numbers

Version is automatically derived from git tags using `setuptools_scm`:
- Tag format: `v{major}.{minor}.{patch}` (e.g., `v1.2.3`)
- Fallback: Version `0.1.0` if no git tag found
- Artifacts use version without 'v' prefix

## Verification Checklist

After a successful release build:

- [ ] All artifact files exist in GitHub Release
- [ ] DMG files are mountable (macOS)
- [ ] ZIP files extract without errors (Windows)
- [ ] TAR.GZ files extract without errors (Linux)
- [ ] SHA256SUMS.txt checksums match all artifacts
- [ ] App launches without errors from extracted artifacts
- [ ] Release notes are present and accurate
