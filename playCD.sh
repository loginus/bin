#!/bin/bash
#Odtwarzanie wyranego nr utworu z plyty
if [[ $# -gt 0 ]]
then
	x="-t $1";
	echo "Playing nr. $1";
else
	x="";
	echo "Playing all tracks";
fi
cdda2wav -q -e $x -d0  -N dev=/dev/hdc -interface cooked_ioctl -x #-p
