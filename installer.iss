#define MyAppName "JARVIS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "JARVIS"
#define MyAppExeName "JARVIS.exe"

[Setup]
AppId={{7C3A8E7F-4D0A-4C8D-9B9F-JARVIS1000}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\JARVIS
DefaultGroupName=JARVIS

OutputDir=C:\JARVIS\installer_output
OutputBaseFilename=JARVIS_Setup

Compression=lzma
SolidCompression=yes

WizardStyle=modern

PrivilegesRequired=admin

UninstallDisplayIcon={app}\JARVIS.exe

ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "C:\JARVIS\dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\JARVIS"; Filename: "{app}\JARVIS.exe"
Name: "{autodesktop}\JARVIS"; Filename: "{app}\JARVIS.exe"

[Run]
Filename: "{app}\JARVIS.exe"; Description: "Launch JARVIS"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"