# Packaging GrowForge for Windows

This produces the two downloadable artifacts published on the
[Releases](https://github.com/MalloyTheDev/growforge/releases) page:

| Artifact | What it is |
|---|---|
| `GrowForge-<version>-windows-x64.zip` | Portable build — unzip and run, no install. |
| `GrowForge-<version>-setup.exe` | Installer — Start Menu shortcut + uninstaller. |

Binaries are **not** committed to the repo; they're attached to GitHub Releases.

## 1. Build a release executable

```sh
cd growforge-qt
cmake -G Ninja -B build -S . -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="C:/Qt/Qt6.11.0/6.11.0/mingw_64" \
  -DCMAKE_CXX_COMPILER="C:/Qt/Qt6.11.0/Tools/mingw1310_64/bin/g++.exe"
cmake --build build
```

## 2. Stage a self-contained bundle with `windeployqt`

```sh
rm -rf dist/GrowForge && mkdir -p dist/GrowForge
cp build/growforge.exe dist/GrowForge/
"C:/Qt/Qt6.11.0/6.11.0/mingw_64/bin/windeployqt.exe" \
  --release --compiler-runtime --no-translations dist/GrowForge/growforge.exe
cp ../LICENSE dist/GrowForge/LICENSE.txt
```

`dist/GrowForge/` is now a folder that runs on any Windows x64 machine without Qt
installed (it includes the Qt and MinGW runtime DLLs and the platform/SQL plugins).

## 3. Portable ZIP

Add the portable-data marker so the build keeps its data alongside the executable,
then zip:

```sh
echo "portable" > dist/GrowForge/portable.txt
powershell -NoProfile -Command \
  "Compress-Archive -Path 'dist/GrowForge' -DestinationPath 'dist/GrowForge-1.0.0-windows-x64.zip' -Force"
rm dist/GrowForge/portable.txt   # keep the bundle clean for the installer
```

## 4. Installer (Inno Setup)

Install [Inno Setup 6.3+](https://jrsoftware.org/isdl.php), then:

```sh
cd packaging
iscc growforge.iss        # output: ../dist/GrowForge-1.0.0-setup.exe
```

The installer deploys to `Program Files\GrowForge`, adds a Start Menu shortcut and an
uninstaller, and (optionally) a desktop icon.

## Data location

- **Installed build:** user data lives in `%LOCALAPPDATA%\GrowForge`
  (`growforge.db`, `photos/`, `exports/`, `backups/`). It is left intact on uninstall.
- **Portable build:** because `portable.txt` sits next to `growforge.exe`, all data is
  kept in that folder instead — move it or run it from a USB drive freely. Delete
  `portable.txt` to switch a portable copy back to the per-user location.

## Code signing & SmartScreen

When you download or run an **unsigned** executable, Windows/Edge SmartScreen shows a
red warning ("isn't commonly downloaded" / "unknown publisher"). This is expected for
any new app that isn't code-signed and has no download reputation yet — it is **not** a
sign anything is wrong with the build. The only way to remove it is to **Authenticode
code-sign** the executables with a trusted certificate.

**Certificate options:**

| Option | Cost | SmartScreen behavior |
|---|---|---|
| **Azure Trusted Signing** | ~$10/mo | Microsoft-run signing service; good reputation. Best value for indie devs. Requires a verified identity. |
| **OV** (Organization Validation) cert | ~$200–400/yr | Removes "unknown publisher"; SmartScreen reputation still builds up over downloads. |
| **EV** (Extended Validation) cert | ~$300–600/yr | **Instant** SmartScreen reputation (no warning on first download). Requires a hardware token / cloud HSM. |
| Self-signed | free | **Does not help distribution** — only trusted on machines that import the cert. |

`signtool.exe` (Windows SDK) is already on this machine; you only need the certificate.

**Sign with [`sign.ps1`](sign.ps1)** — sign the app exe *before* building the installer,
then sign the installer:

```powershell
# 1. build + windeployqt into dist\GrowForge  (steps 1–2 above)
# 2. sign the app executable
powershell -ExecutionPolicy Bypass -File packaging\sign.ps1 -Pfx C:\path\cert.pfx -Password **** `
  -Files dist\GrowForge\growforge.exe
# 3. build the installer (step 4), which now packages the signed exe
cd packaging; iscc growforge.iss; cd ..
# 4. sign the installer itself
powershell -ExecutionPolicy Bypass -File packaging\sign.ps1 -Pfx C:\path\cert.pfx -Password **** `
  -Files dist\GrowForge-1.0.0-setup.exe
```

(With a cert installed in the Windows store, use `-Thumbprint <sha1>` instead of `-Pfx`.)
The script SHA-256 signs with an RFC-3161 timestamp and verifies each file. The `.zip` is
not signable, but the `growforge.exe` inside it is.

## Publishing a release

```sh
gh release create v1.0.0 \
  dist/GrowForge-1.0.0-windows-x64.zip \
  dist/GrowForge-1.0.0-setup.exe \
  --title "GrowForge 1.0.0" --notes-file notes.md
```
