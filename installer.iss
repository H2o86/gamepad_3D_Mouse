; Inno Setup Script for SolidMouse - Unified 3D SpaceMouse for SolidWorks
#define MyAppName "SolidMouse"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "H2o86"
#define MyAppURL "https://github.com/H2o86/gamepad_3D_Mouse"
#define MyAppExeName "SolidMouse.exe"

[Setup]
AppId={{D1CCE398-4C12-40DB-B38F-DF2AF5F409E7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_dist
OutputBaseFilename=SolidMouse_Setup_v1.0.0
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostarticon"; Description: "Run on Windows Startup (Tự động chạy cùng Windows)"; GroupDescription: "Startup Settings:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "lang.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "sw_shortcuts.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostarticon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall nowait skipifsilent
