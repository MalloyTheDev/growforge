<#
  Authenticode-sign GrowForge executables.

  This is what makes Windows/SmartScreen stop showing the "unknown publisher" /
  red download warning. It requires a real code-signing certificate (see the
  "Code signing & SmartScreen" section of README.md) — signtool itself ships with
  the Windows SDK and is located automatically.

  Usage:
    # certificate file (.pfx):
    .\sign.ps1 -Pfx "C:\path\to\cert.pfx" -Password "****"
    # or a certificate already installed in the Windows cert store:
    .\sign.ps1 -Thumbprint "A1B2C3...."
    # sign specific files instead of the default release artifacts:
    .\sign.ps1 -Thumbprint "..." -Files ..\dist\GrowForge\growforge.exe

  Recommended order: sign dist\GrowForge\growforge.exe BEFORE building the
  installer (so the installed/portable exe is signed), then run iscc, then run
  this again on dist\GrowForge-<ver>-setup.exe.
#>
[CmdletBinding()]
param(
  [string]$Pfx,
  [string]$Password,
  [string]$Thumbprint,
  [string[]]$Files,
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)
$ErrorActionPreference = "Stop"

# --- locate signtool.exe (prefer the newest x64 build from the Windows SDK) ---
$signtool = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $signtool) { $signtool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source }
if (-not $signtool) { throw "signtool.exe not found. Install the Windows 10/11 SDK." }
Write-Host "Using $signtool"

# --- default to the standard release artifacts if none specified ---
$dist = Join-Path $PSScriptRoot "..\dist"
if (-not $Files -or $Files.Count -eq 0) {
  $candidates = @(
    (Join-Path $dist "GrowForge\growforge.exe"),
    (Get-ChildItem (Join-Path $dist "GrowForge-*-setup.exe") -ErrorAction SilentlyContinue | ForEach-Object FullName)
  )
  $Files = $candidates | Where-Object { $_ -and (Test-Path $_) }
}
if (-not $Files -or $Files.Count -eq 0) { throw "No files to sign. Build the release first." }

# --- authentication: cert store thumbprint or .pfx file ---
if ($Thumbprint)  { $auth = @("/sha1", $Thumbprint) }
elseif ($Pfx)     { $auth = @("/f", $Pfx); if ($Password) { $auth += @("/p", $Password) } }
else { throw "Provide -Thumbprint (cert in the Windows store) or -Pfx [-Password]." }

$common = @("/fd", "SHA256", "/tr", $TimestampUrl, "/td", "SHA256", "/v")

foreach ($f in $Files) {
  Write-Host "`n== Signing $f =="
  & $signtool sign @common @auth $f
  if ($LASTEXITCODE -ne 0) { throw "Signing failed for $f" }
  & $signtool verify /pa /v $f
  if ($LASTEXITCODE -ne 0) { throw "Verification failed for $f" }
}
Write-Host "`nAll files signed and verified."
