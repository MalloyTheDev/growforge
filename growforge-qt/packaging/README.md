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

## Publishing a release

```sh
gh release create v1.0.0 \
  dist/GrowForge-1.0.0-windows-x64.zip \
  dist/GrowForge-1.0.0-setup.exe \
  --title "GrowForge 1.0.0" --notes-file notes.md
```
