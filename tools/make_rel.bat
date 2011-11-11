@echo off
REM this is for generating fully optimized bytecode

setlocal
REM NOTE: Modify this path to suit your need
set GINGERPRAWN_ROOT=E:\kodez\svnmain\gingerprawn

REM FIXME this flushes any other user-defined PYTHONPATH
set PYTHONPATH=%GINGERPRAWN_ROOT%

REM go to the file's original residence
REM UPDATE: interface dir got renamed!
REM UPDATE AGAIN: that dir is re-renamed so I decided to separate that
set LAUNCHER_NAME=launcher

cd %GINGERPRAWN_ROOT%\%LAUNCHER_NAME%

echo =======================================
echo Generating gingerprawn release binaries
echo =======================================
echo.

echo py2exe-ing %LAUNCHER_NAME%.
echo ---------------------
python -OO setup_rel.py py2exe > NUL
echo ok.
echo.

cd dist

echo UPX-ing result binaries.
echo ------------------------
upx -9v *.pyd *.dll *.exe
echo all done.
echo.

echo Copying extra files.
echo --------------------

echo splash.png
copy ..\splash.png . > NUL

echo __init__.pyo
copy ..\__init__.pyo . > NUL

echo done.
echo.

echo Trimming library archive.
echo -------------------------
echo.

echo Extracting...
7z x -olibrary library.zip > NUL
cd library

echo Removing extra gingerprawn files...
rd /S /Q gingerprawn

echo Repackaging...
7z a library_new.zip * > NUL

echo Replacing original archive...
copy .\library_new.zip ..\library.zip

echo Cleaning up...
cd ..
rd /S /Q library
echo done.
echo.

cd ..

echo ==========
echo Completed!
echo ==========

pause

endlocal
