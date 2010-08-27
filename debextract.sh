#!/bin/sh
echo "Usage:"
echo "debextract.sh packagename.deb"

ar p $1 data.tar.gz | tar zvx

