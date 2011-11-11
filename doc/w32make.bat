@echo off

setlocal
REM change this if you'd like to use this tool
set PYTHONPATH=E:\kodez\svnmain\gingerprawn

.\make.bat %*
explorer build

endlocal
