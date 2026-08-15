# Windows code signing

PanoViewer's release workflow supports optional Authenticode signing. Builds remain reproducible and publish normally when no certificate is configured, but Windows may show a SmartScreen warning for unsigned downloads.

## Required GitHub Actions secrets

- `WINDOWS_CERTIFICATE`: the Base64 representation of a code-signing PFX file
- `WINDOWS_CERTIFICATE_PASSWORD`: the PFX password

Generate the Base64 value locally in PowerShell without committing the certificate:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('PanoViewer-signing.pfx')) | Set-Clipboard
```

Add both values under repository **Settings → Secrets and variables → Actions**. Never commit the PFX, password, Base64 value, or exported private key.

On a tagged release, the workflow imports the certificate into the ephemeral runner, signs `PanoViewer.exe` with SHA-256 and a trusted timestamp, verifies the signature, and only then creates `SHA256SUMS.txt` and uploads the release assets.

## Certificate choice

Use a certificate issued for public code signing by a trusted certificate authority. Organization-validation and extended-validation certificates have different identity verification, hardware, and reputation requirements; confirm current requirements with the certificate provider before purchasing.
