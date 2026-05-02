# Releasing

Versions come from **git tags** via `setuptools-scm` (see `pyproject.toml`). Tag with `vMAJOR.MINOR.PATCH` to align with Conventional Commits.

## Local build

```bash
pip install -e ".[dev,packaging]"
python packaging/build.py --target pyinstaller
```

Artifacts land under `packaging/dist/` (gitignored). Install PyInstaller via the `packaging` extra.

## macOS signing & notarization

GitHub Actions can codesign and notarize when repository secrets are configured (`APPLE_DEVELOPER_ID`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_PASSWORD`). Without secrets, workflows still produce **unsigned** bundles for contributors.

## Branch protection (recommended)

- Require PR + CI (`lint`, `test`, `preflight`) before merge to `main`.
- Protect version tags; restrict who can push tags if using automated release bots.

## Release artifacts

The repository includes workflow sketches for multi-platform installers (`.dmg`, `.exe`, `.AppImage`). Tune matrix runners and signing steps to match your certificate setup.
