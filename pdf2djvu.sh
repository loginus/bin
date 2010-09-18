#!/bin/bash
FILES=$@
function generate_new_name { 
	OLD=$1
	NAME=$OLD".djvu"
	NO=0
	while [ -e $NAME ]
	do
		let NO=NO+1
		NAME=$OLD".djvu."$NO
	done
	echo $NAME;
	
}
for OLDFILENAME in $@
do
	echo $OLDFILENAME
	NEWNAME=`generate_new_name "$OLDFILENAME"`
	echo $NEWNAME
	pdf2djvu "$OLDFILENAME" -o "$NEWNAME"
done
