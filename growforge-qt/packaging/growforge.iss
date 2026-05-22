; GrowForge — Inno Setup installer script
; Build with:  iscc growforge.iss   (from this packaging/ directory)
; Requires Inno Setup 6.3+  (https://jrsoftware.org/isdl.php)
;
; Prerequisite: the deployed application bundle must exist at ..\dist\GrowForge\
; (produced by build/growforge.exe + windeployqt — see packaging/README.md).

#define MyAppName "GrowForge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Brendan Malloy"
#define MyAppURL "https://github.com/MalloyTheDev/growforge"
#define MyAppExeName "growforge.exe"
#define BundleDir "..\dist\GrowForge"

[Setup]
AppId={{7B2E9A4C-C4C3-465C-A66B-510CD99453F4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=..\..\LICENSE
OutputDir=..\dist
OutputBaseFilename=GrowForge-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Deploy the entire windeployqt bundle, but never the portable-data marker
; (installed builds keep user data in %LOCALAPPDATA%\GrowForge).
Source: "{#BundleDir}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion; Excludes: "portable.txt,growforge.db,growforge.db-*"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; Note: user data in %LOCALAPPDATA%\GrowForge is intentionally left in place on
; uninstall so a reinstall keeps your grow history.
