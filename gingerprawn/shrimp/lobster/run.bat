@DEL lobster.zip.bak 2> NUL
@REN lobster.zip lobster.zip.bak
@7z a lobster.zip *.py > NUL
@python "..\..\launcher\main.py"
