#!/bin/sh
# Organises photos manually downloaded from digital camera
# Creates directory for each day
# and moves photos to relevant directory

TIMESTAMP="timestamp" #english version
exiv2 | grep "Manipulowanie" && TIMESTAMP="Znacznik czasu" # polish version

for x in $@
do
DIR=`exiv2 "$x" | grep $TIMESTAMP | awk '{print $4}' | sed 's/:/_/g'`
if [ ! -d $DIR ]
then
	mkdir $DIR
	echo "$DIR nie istnieje"
else
	echo "$DIR istnieje"
fi
mv -v "$x" $DIR/
done
