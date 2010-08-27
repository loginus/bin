#!/bin/sh
function help {
	echo "Usage: subtranslate.sh -i input_file -l language";
	echo "Example: subtranslate.sh -i studniowka.cze.srt -l cze";
}

while getopts  "i:l:" FLAG
do
	case $FLAG in 
		"i") INPUT="$OPTARG"; echo $OPTARG ;;
		"o") LANGUAGE="$OPTARG"; echo $OPTARG ;;
		*) help; exit
	esac
done
if [[ -z $INPUT ]]
then
	echo "Input parameter is missing";
	help
	exit
fi

LANGUAGES[a]="cp1250"
LANGUAGES[b]="cp1250"
LANGUAGES[c]="cp1250"
LANGUAGES[d]="cp1252"
LANGUAGES[e]="cp1252"

echo "LANG $LANGUAGE"
echo ${LANGUAGES[b]}
