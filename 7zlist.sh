#!/bin/bash
 7z l $1 2>/dev/null |sed -e '1,/-----/d
/----/,$d
s/\\/\//g' | awk '{name=$6; if (name=="") name=$5; print $1" "$2" rw-r--r-- "$4" "name;}';
