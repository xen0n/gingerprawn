#!/bin/bash
rm lobster.zip.bak 2> /dev/null
mv lobster.zip lobster.zip.bak
7z a lobster.zip *.py > /dev/null
python ../../launcher/main.py
# vi:ff=unix
