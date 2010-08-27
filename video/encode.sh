#!/bin/bash
#INPUT="dvd://1 -dvd-device studniowka2.iso";
#OUTPUT="studniowka2.avi";
#BITRATE=1020;
function help {
        echo "Usage: encode.sh -i input_file [-o output_file -b bitrate]";
        echo "Example: encode.sh -i "dvd://1 -dvd-device=/dev/cdrom" -o studniowka.wav -b 1024";
}

while getopts  "i:o:b:2" FLAG
do
        case $FLAG in
                "i") INPUT="$OPTARG";;
                "o") OUTPUT="$OPTARG";;
                "b") BITRATE="$OPTARG";;
                "2") ONLY2PASS=1;;
                *) help; exit
        esac
done
if [ -z $INPUT ]
then
        echo "Input file option is missing"
        help
        exit
fi

if [[ $ONLY2PASS -ne 1 ]]
then

	if [ -f divx2pass.log ]
	then
		echo "File divx2pass.log already exists in current directory"
		TIMESTAMP=`date +%Y%m%d%H%M%S%N`
		mv -i divx2pass.log $TIMESTAMP-divx2pass.log
		echo "Bacup saved in $TIMESTAMP-divx2pass.log";
	fi

	echo "ENCODING 1 PASS input: $INPUT"
	DUMMY_BITRATE=700
	mencoder -nosound $INPUT -o /dev/null  -ovc x264 -x264encopts bitrate=$DUMMY_BITRATE:pass=1:subq=1:frameref=1; 
fi
if [[ -z $OUTPUT || -z $BITRATE ]]
then
       	echo "Output file or bitrate not specified";
        echo "Encoding finished after first pass";
       	exit
fi
echo "ENCODING 2 PASS output: $INPUT birate: $BITRATE"
#mencoder -nosound "$INPUT" -o "$OUTPUT"  -ovc x264 -x264encopts bitrate=$BITRATE:pass=2:subq=6:partitions=all:8x8dct:me=umh:frameref=5:bframes=3:b_pyramid:weight_b;
mencoder -nosound $INPUT -o "$OUTPUT"  -ovc x264 -x264encopts bitrate=$BITRATE:pass=2:subq=6:frameref=15:partitions=all:me=umh;
