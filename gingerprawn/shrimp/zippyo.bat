@echo Zipping all shrimp pyo files...
@for /d %%i in (*) do @echo %%i && cd %%i && del %%i_pyo.zip 2> nul && 7z a %%i_pyo.zip *.pyo > nul && cd ..
@echo all done
@echo.
@rem vi:ai:et:ts=4 sw=4 sts=4 ff=unix fenc=utf-8
