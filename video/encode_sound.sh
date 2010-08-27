#!/bin/bash

#INPUT="dvd://1 -dvd-device studniowka2.iso";
#OUTPUT="studniowka4.wav";

function help {
	echo "Usage: encode_sound.sh -i input_file -o output_file";
	echo "Example: encode_sound.sh -i 'dvd://1 -dvd-device=/dev/cdrom' -o studniowka.wav";
	echo "Example: encode_sound.sh -r -i MVI_6543.AVI -o studniowka.wav";
}

RAW=0
while getopts  "i:o:s:r" FLAG
do
	case $FLAG in 
		"i") INPUT="$OPTARG"; echo $OPTARG ;;
		"o") OUTPUT="$OPTARG"; echo $OPTARG ;;
		"s") SPECIAL="$OPTARG"; echo $OPTARG ;;
		"r") RAW=1; echo "Raw mode" ;;
		*) help; exit
	esac
done
if [[ -z $INPUT || -z $OUTPUT ]]
then
	echo "One of parameteres is missing";
	help
	exit
fi

mkfifo "$OUTPUT"
if [[ $RAW -eq 1 ]]
then
  	echo "Raw mode encoding";
  	oggenc $SPECIAL -Q -r -B 16 -C 2 -R 48000 "$OUTPUT" &
	mplayer -format s16le -vc null -vo null -ao pcm:fast:file="$OUTPUT" "$INPUT"
else
  	echo "Normal mode encoding";
	oggenc $SPECIAL --quiet "$OUTPUT" &
	mplayer -vc null -vo null -ao pcm:file="$OUTPUT" "$INPUT" 
fi
if [ $? -eq 0 ]
then
	echo "File encoded successfully!" 
	rm $OUTPUT
else
	echo "Something goes wrong. Please try again"
fi
