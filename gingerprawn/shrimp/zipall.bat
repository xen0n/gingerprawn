@echo Zipping all shrimp...
@for /d %%i in (*) do @echo %%i && cd %%i && del %%i.zip 2> nul && 7z a %%i.zip *.py > nul && cd ..
@echo all done
@echo.
@rem vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8
