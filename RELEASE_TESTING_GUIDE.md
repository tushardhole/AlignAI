# AlignAI Release Testing Guide

## What We've Built

A complete multi-platform automated build system for AlignAI that creates distributable artifacts for:

- **macOS**: arm64 (Apple Silicon) + x86_64 (Intel) → DMG format
- **Windows**: x64 + arm64 → Installer format (currently ZIP, ready for NSIS)
- **Linux**: x86_64 + arm64 → Archive format (currently TAR.GZ, ready for AppImage)

## Current Status

✅ **Completed**:
- build-test.yml workflow for manual testing
- Enhanced build.py supporting all platforms
- Packaging/signer.py for macOS code signing
- Updated release.yml for production releases
- Comprehensive documentation (BUILD_SYSTEM.md)

🏗️ **In Progress**:
- Build-test workflow running on all platforms (currently queued/in_progress)

## How to Test

### Step 1: Wait for Build-Test Workflow to Complete

The workflow is currently running. Check progress:

```bash
# View current status
gh run list --workflow=build-test.yml --limit 1

# View detailed jobs
gh run view 25409943728 --json jobs --jq '.jobs[] | {name: .name, status: .status}'

# View artifacts once complete
gh run view 25409943728
```

Expected job results:
- ✅ Build (macos-14 / arm64) → AlignAI-*-arm64.dmg
- ✅ Build (macos-13 / x86_64) → AlignAI-*-x86_64.dmg
- ✅ Build (windows-latest / x64) → AlignAI-*-Setup-x64.zip
- ✅ Build (ubuntu-22.04 / x86_64) → AlignAI-*-x86_64.tar.gz

### Step 2: Download Artifacts

Once workflow completes:

1. Go to: https://github.com/tushardhole/AlignAI/actions/workflows/build-test.yml
2. Click on the latest run
3. Download artifacts for each platform:
   - `dist-macos-14-arm64`
   - `dist-macos-13-x86_64`
   - `dist-windows-latest-x64`
   - `dist-ubuntu-22.04-x86_64`

### Step 3: Test on Each Platform

**macOS (Recommended - you can test now):**
```bash
# 1. Mount and test the DMG
open dist-installers/AlignAI-*.dmg

# 2. Drag app to Applications (optional, can run from mounted volume)
# 3. Launch AlignAI from Applications or mounted volume
# 4. Verify app starts without errors
```

**Windows (when available):**
```powershell
# 1. Extract the ZIP
Expand-Archive -Path AlignAI-*-Setup-x64.zip

# 2. Run the extracted application
./alignai/alignai.exe

# 3. Verify GUI appears and is responsive
```

**Linux (when available):**
```bash
# 1. Extract the archive
tar -xzf AlignAI-*-x86_64.tar.gz

# 2. Run the executable
./alignai/alignai

# 3. Verify GUI appears (requires X11/Wayland)
```

### Step 4: Verify Checksums (Optional)

If SHA256SUMS.txt is present in artifacts:

```bash
# Download SHA256SUMS.txt from artifacts
# Then verify:
sha256sum -c SHA256SUMS.txt

# Or manually:
sha256sum AlignAI-*.dmg
```

### Step 5: Create a Real Release (Optional)

Once you're satisfied with the test workflow:

```bash
# Create a release tag (replaces v0.1.0)
git tag -a v0.2.0 -m "Second release: Multi-platform builds

- Automated builds for macOS (Intel + Apple), Windows, Linux
- All builds include proper code signing support
- Release artifacts available for all architectures"

# Push the tag - this triggers the release.yml workflow
git push origin v0.2.0

# Monitor the release workflow
gh run list --workflow=release.yml --limit 1
```

Once release.yml completes, check GitHub Releases:
- https://github.com/tushardhole/AlignAI/releases/tag/v0.2.0

You should see:
- DMG files (macOS)
- ZIP files (Windows)
- TAR.GZ files (Linux)
- SHA256SUMS.txt
- sbom.spdx.json (Software Bill of Materials)
- Release notes

## Troubleshooting Build Issues

### Build Status Unknown
```bash
# Get the run ID
RUN_ID=$(gh run list --workflow=build-test.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# View full logs
gh run view $RUN_ID --log
```

### Building Locally for Quick Tests
If you want to build locally without waiting for GitHub Actions:

```bash
# Build PyInstaller app bundle
python packaging/build.py --target pyinstaller

# On macOS: Create DMG
python packaging/build.py --target dmg

# Results in dist-installers/
ls -lh dist-installers/
```

## Next Steps

### For Testing:
1. ✅ Wait for build-test workflow to complete
2. ⏳ Download and extract artifacts
3. ⏳ Test on each platform (especially macOS)
4. ⏳ Verify app launches and is responsive

### For Production Release:
1. After testing completes successfully
2. Create v0.2.0 release tag
3. Push tag to trigger release.yml
4. Wait for release.yml to complete
5. Verify all artifacts in GitHub Releases
6. Share release link: https://github.com/tushardhole/AlignAI/releases

### For macOS Code Signing (Optional):
To enable notarization for App Store distribution:

1. Set GitHub Secrets in repository settings:
   - `APPLE_DEVELOPER_ID`: Your Developer ID certificate
   - `APPLE_ID`: Your Apple ID email
   - `APPLE_TEAM_ID`: Your Team ID
   - `APPLE_APP_PASSWORD`: App-specific password

2. When these are set, release.yml will automatically:
   - Code sign the DMG
   - Submit for notarization
   - Verify notarization status

## Monitoring Builds

Check progress in real-time:

```bash
# Watch build-test workflow
watch -n 30 'gh run list --workflow=build-test.yml --limit 1'

# Or check specific platform
gh run view 25409943728 --json jobs \
  --jq '.jobs[] | select(.name | contains("macos-14"))'
```

## Files Modified

Core changes made to enable multi-platform builds:

- `.github/workflows/build-test.yml` - NEW: Manual test workflow
- `.github/workflows/release.yml` - UPDATED: Integrated with new build.py
- `packaging/build.py` - UPDATED: Enhanced with platform targets
- `packaging/signer.py` - NEW: macOS code signing support
- `packaging/icons/` - NEW: Placeholder icon assets
- `pyproject.toml` - UPDATED: Build dependencies
- `BUILD_SYSTEM.md` - NEW: Technical documentation

## Success Criteria

Build-test workflow is successful when:

✅ All 4 platform jobs complete with status "completed"
✅ All jobs have conclusion "success"
✅ Artifacts download without errors
✅ Checksums match (if present)
✅ Apps launch and respond to input on respective platforms

---

**Questions?** See BUILD_SYSTEM.md for technical details.
