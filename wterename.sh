#!/bin/bash
for x in $@
do
	BASE_NAME=`echo "$x" | sed -e 's/^[a-z]\+_[0-9]\+-*//'`
	TIMESTAMP=`date "+%Y%m%d%H%M%S" -r "$x"`
	mv -v "$x" "wte_"$TIMESTAMP"-"$BASE_NAME
done
