for /r %%i in (migrations\*.py) do @if not "%%~nxi"=="__init__.py" del "%%i"
for /r %%i in (migrations\*.pyc) do @if exist "%%i" del "%%i"