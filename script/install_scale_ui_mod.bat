@ECHO OFF

REM This is here in case someone needs to hardcode a path ( Just remove the REM keywords, below this line )
REM SET python_path=C:\Program Files\GIMP 2\bin\python
REM IF EXIST "%python_path%.exe" (
REM     "%python_path%" install_scale_ui_mod.py
REM     GOTO :EOF
REM )

SET python_loc="\bin\python" "\32\bin\python" "\Python\python"
SET gimp_loc="%userprofile%\AppData\Local\Programs\GIMP" "%programfiles(x86)%\GIMP" "%programfiles%\GIMP" "%userprofile%\AppData\Local\Programs\GIMP 2" "%programfiles(x86)%\GIMP 2" "%programfiles%\GIMP 2"

SETLOCAL ENABLEDELAYEDEXPANSION
FOR %%a in (%gimp_loc%) DO (
    FOR %%b in (%python_loc%) DO (
        SET python_path=%%~a%%~b
        IF EXIST "!python_path!.exe" (
            "!python_path!" install_scale_ui_mod.py
            GOTO :EOF
        )
    )
)