#!/bin/bash
bash kompOGG &
if [[ $# -eq 0 ]]
then
	cdda2wav -x -P 3 -B -I cooked_ioctl dev=/dev/hdc
else
	for x in $@
	do
		cdda2wav -x -P 3 -t $x -I cooked_ioctl dev=/dev/hdc
		mv audio.wav audio_$x.wav
	done
fi
