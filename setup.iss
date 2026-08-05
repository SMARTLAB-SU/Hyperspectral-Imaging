; Inno Setup Script for Hyperspectral Imaging System
; Use Inno Setup Compiler (on Windows) to compile this script into a standalone installer (.exe).

#define MyAppName "Hyperspectral Imaging System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sanjivani"
#define MyAppExeName "HyperspectralImaging.exe"

[Setup]
AppId={{D37F2C0B-97EE-4D2A-A04A-7A7A5D07E8E4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; "lowest" allows installation without administrator privileges (current user installation).
; Change to "admin" if you want to install for all users on the computer.
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=HyperspectralImaging_Setup
SetupIconFile=sanjivani.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main Executable
Source: "HyperspectralImaging.exe"; DestDir: "{app}"; Flags: ignoreversion
; Assets and resources
Source: "sanjivani.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "SETUP_INSTRUCTIONS.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "USER_MANUAL.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "shared\*"; DestDir: "{app}\shared"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{autodesktop}\{#MyAppName} Data"; Filename: "{app}\HyperspectralImaging_Data"; Tasks: desktopicon

[Dirs]
Name: "{app}\HyperspectralImaging_Data"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
