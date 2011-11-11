#!/bin/bash
echo Zipping all shrimp...
for name in `ls -1`; do
	if [ -d $name ]; then
		echo $name;
		(cd $name; 7z a $name.zip *.py > /dev/null; );
	fi;
done
echo all done
echo
