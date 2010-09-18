#!/bin/bash
#S³u¿y do nagrywania p³ytek :]
CDDRIVE="/dev/hdb";
#CDDRIVE="0,0,0";
SPEED=52;
if [[ $# -lt 1 ]]
then
	echo "B³±d: Brak obrazu ISO do wypalenia";
	exit;
else
	#podano obraz
	echo "Obliczam rozmiar obrazu";
	filesize=$(ls -l "$1" | awk '{print $5}') || exit;
	echo "Obliczam sumê kontorln±";
	time md5sum=$(md5sum "$1" | awk '{print $1}') || exit;	
	echo "Rozmiar obrazu do wypalenia $filesize md5 $md5sum";
	if [[ $filesize -gt 730000000 ]]
	then
		opcje="-overburn";
		echo "U¿yjê ocji overburn";
	else
		opcje="";
	fi
	echo $opcje;
	sleep 2;
	echo "Nagrywam...";
	time cdrecord -v minbuf=95 speed=$SPEED -sao fs=12m driveropts=burnfree -eject dev=$CDDRIVE $opcje "$1" || exit
	echo "Obliczam sumê kontorln± p³yty";
	time md5sum2=$(md5sum $CDDRIVE | awk '{print $1}') || exit;	
	echo "Suma kontrolna wypalonych danych $md5sum2 a obrazu $md5sum";
	if [[ $md5sum = $md5sum2 ]]
	then
		echo "Hurra uda³o siê!";
		rm "$1" && echo "plik obrazu usuniety"
	else
		echo "Sumy si± nie zgadzaj± :'( spróbuj raz jeszcze.";
	fi
	eject $CDDRIVE;
fi
