#define MyAppName "JARVIS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "JARVIS"
#define MyAppExeName "JARVIS.exe"

[Setup]
AppId={{7B7C28D2-EB44-4F40-9BB9-61EB72A58761}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\Programs\JARVIS
DefaultGroupName=JARVIS

OutputDir=C:\JARVIS\installer_output
OutputBaseFilename=JARVIS-Setup

Compression=lzma2
SolidCompression=yes

PrivilegesRequired=lowest

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

WizardStyle=modern

UninstallDisplayName=JARVIS
UninstallDisplayIcon={app}\JARVIS.exe

CloseApplications=yes
RestartApplications=no

SetupLogging=yes

[Files]
Source: "C:\JARVIS\dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\JARVIS.exe"
Name: "{autodesktop}\JARVIS"; Filename: "{app}\JARVIS.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\JARVIS.exe"; Description: "Launch JARVIS"; Flags: nowait postinstall skipifsilent