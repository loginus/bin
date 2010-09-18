#!/bin/bash


for x in $( grep "HOMEPAGE" $1/*| awk -F '"' '{print $2}' | sort -u)
do
	if [ $(/usr/lib/mozilla/mozilla-bin -remote "ping()") ]
	then
		mozilla -remote "openURL($x,new-tab)"
	else
		/usr/lib/mozilla/mozilla-bin $x &
	fi
done
	
