#define MyAppName "WinTrack"
#define MyAppVersion "0.0.2"
#define MyAppPublisher "Srikanth"
#define MyAppURL "https://github.com/sr1k7nth/WinTrack"
#define MyAppExeName "WinTrack.exe"

[Setup]
AppId={{2B60F0B7-89BF-4D53-ADC6-17697FB85253}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableDirPage=yes
DisableProgramGroupPage=yes

CloseApplications=yes
RestartApplications=yes

OutputDir=C:\Users\Srikanth\Downloads
OutputBaseFilename=WinTrack Installer
SetupIconFile=C:\Users\Srikanth\projects\WinTrack\media\setup_logo.ico

Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Files]
Source: "dist\WinTrack\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch WinTrack"; Flags: nowait postinstall skipifsilent