# Contributing to PanoViewer

Thank you for helping improve PanoViewer. Bug reports, documentation improvements, translations, test panoramas, and code contributions are welcome.

## Before opening an issue

- Check existing issues and try the latest release.
- For bugs, include operating system, browser, image format and dimensions, reproduction steps, and screenshots when possible.
- Do not post private panorama photos or security vulnerabilities in a public issue.

## Pull requests

1. Fork the repository and create a focused branch.
2. Keep user-facing behavior and documentation in sync.
3. Build the standalone HTML and Windows executable.
4. Test all four modes with `tools/test_pano.png`.
5. Describe what changed, why, and how it was verified.

```powershell
python scripts\build.py --embed tools\test_pano.png
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

By contributing, you agree that your contribution may be distributed under the project's MIT License.
