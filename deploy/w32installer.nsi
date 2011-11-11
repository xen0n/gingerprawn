; gingerprawn setup script
; -*- coding: gbk -*-

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "江大侠 0.1.0 alpha 1 内部测试版"
  OutFile "gingerprawn-0.1.0a1.exe"

  !packhdr "$%TEMP%\exehead.tmp" '"upx.exe" -9 "$%TEMP%\exehead.tmp"'

  SetCompressor /SOLID lzma
  SetCompressorDictSize 16

  ;Default installation folder
  InstallDir "$APPDATA\江大侠"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\GingerPrawn" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

  BrandingText "江大侠，江南大学校园生活客户端"

;--------------------------------
;Variables

  Var StartMenuFolder

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Language Selection Dialog Settings

  ;Remember the installer language
  !define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
  !define MUI_LANGDLL_REGISTRY_KEY "Software\GingerPrawn"
  !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE ".\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\GingerPrawn"
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "江大侠"

  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English" ;first language is the default language
  !insertmacro MUI_LANGUAGE "SimpChinese"


;--------------------------------
;Reserve Files

  ;If you are using solid compression, files that are required before
  ;the actual installation should be stored first in the data block,
  ;because this will make your installer start faster.

  !insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
;Installer Functions

Function .onInit

  !insertmacro MUI_LANGDLL_DISPLAY

FunctionEnd

;--------------------------------
;Installer Sections

InstType "Full"
; InstType "minimal"


Section "江大侠主体文件" SecInfrastructure
  SectionIn 1 RO

  SetOutPath "$INSTDIR"

  ;ADD YOUR OWN FILES HERE...
  SetOutPath $INSTDIR\gingerprawn
  File ..\gingerprawn\__init__.pyo
  File ..\gingerprawn\__version__.pyo

  ; the former interface dir got renamed just before DVCS migration, just for keeping history
  SetOutPath $INSTDIR\gingerprawn\launcher
  File ..\gingerprawn\launcher\dist\*.*

  SetOutPath $INSTDIR\gingerprawn\api
  File /r ..\gingerprawn\api\*.pyo

  SetOutPath $INSTDIR\gingerprawn\conf
  File /oname=gingerprawn-api-logger.ini ..\gingerprawn\conf\gingerprawn-api-logger.ini.production

  SetOutPath $INSTDIR\gingerprawn\logs

  SetOutPath $INSTDIR\gingerprawn\shrimp
  SetOutPath $INSTDIR\gingerprawn\shrimp\lobster
  File /oname=lobster.zip ..\gingerprawn\shrimp\lobster\lobster_pyo.zip

  SetOutPath $INSTDIR\gingerprawn\shrimp\academic
  File /oname=academic.zip ..\gingerprawn\shrimp\academic\academic_pyo.zip

  ;Store installation folder
  WriteRegStr HKCU "Software\GingerPrawn" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
	CreateShortCut "$SMPROGRAMS\$StartMenuFolder\江大侠.lnk" "$INSTDIR\gingerprawn\launcher\winmain.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecInfrastructure ${LANG_ENGLISH} "Basic files (needed)."
  LangString DESC_SecInfrastructure ${LANG_SIMPCHINESE} "江大侠基础架构，必须安装"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecInfrastructure} $(DESC_SecInfrastructure)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...

  Delete "$INSTDIR\gingerprawn\conf\gingerprawn-api-logger.ini"
  RMDir "$INSTDIR\gingerprawn\conf"

  RMDir /r "$INSTDIR\gingerprawn\api"
  RMDir /r "$INSTDIR\gingerprawn\launcher"
  RMDir /r "$INSTDIR\gingerprawn\shrimp"
  RMDir /r "$INSTDIR\gingerprawn\logs"
  Delete "$INSTDIR\gingerprawn\__init__.pyo"
  Delete "$INSTDIR\gingerprawn\__version__.pyo"
  RMDir "$INSTDIR\gingerprawn"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\江大侠.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  DeleteRegKey /ifempty HKCU "Software\GingerPrawn"

SectionEnd

;--------------------------------
;Uninstaller Functions

Function un.onInit

  !insertmacro MUI_UNGETLANGUAGE

FunctionEnd

; vim:ai:et:ts=2 sw=2 sts=2 ff=unix fenc=gbk
