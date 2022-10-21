; Script generated by the Inno Script Studio Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{76D0C217-8037-4198-8602-75F7C9565A34}
AppName=BinBuilder
AppVersion=1.0.0
;AppVerName=BinBuilder 1.0.0
AppPublisher=Erik K. Nyquist
AppPublisherURL=http://www.ekn.io
AppSupportURL=http://www.ekn.io
AppUpdatesURL=http://www.ekn.io
DefaultDirName={pf}\BinBuilder
DefaultGroupName=BinBuilder
OutputBaseFilename=install-binbuilder-1.0.0
SetupIconFile=C:\Users\Gamer\binbuilder\binbuilder\images\icon.ico
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\Gamer\binbuilder\dist\BinBuilder\BinBuilder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Gamer\binbuilder\dist\BinBuilder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\BinBuilder"; Filename: "{app}\BinBuilder.exe"; IconFilename: {app}\images\icon.ico
Name: "{commondesktop}\BinBuilder"; Filename: "{app}\BinBuilder.exe"; IconFilename: {app}\images\icon.ico; Tasks: desktopicon

[Run]
Filename: "{app}\BinBuilder.exe"; Description: "{cm:LaunchProgram,BinBuilder}"; Flags: nowait postinstall skipifsilent
