#!/bin/bash
FILM=$1
TYTUL=$2

GEEXBOX_OUT_DIR=/tmp/geexbox-generator-1.0.i386
GEEXBOX_IN=/home/wojtek/geexbox-generator-1.0.i386.tar.bz2

if [ -z "$TYTUL" ]
then
	TYTUL=`basename "$FILM" .ogm`
	TYTUL=`basename "$TYTUL" .avi`
	TYTUL=`basename "$TYTUL" .mkv`
fi
if [ ! -d $GEEXBOX_OUT_DIR ]
then
	cd `dirname $GEEXBOX_OUT_DIR`
	echo "Extracting geexbox binaries to $GEEXBOX_OUT_DIR"
	tar -xjf $GEEXBOX_IN
	cd -
fi


cp -v "$FILM" $GEEXBOX_OUT_DIR/iso/
cd $GEEXBOX_OUT_DIR
./generator.sh -t "$TYTUL" -o "$TYTUL".iso
if  isovfy -i "$TYTUL".iso 
then
	rm -v iso/`basename "$FILM"`
else
	echo "Creating ISO image failed"
fi
