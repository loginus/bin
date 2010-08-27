#!/bin/bash
DVD_PATH='~/Wideo/Scarface_dvd/Scarface 1932/'
exit
#manipulate with 
#-T 1,-1 - may be different chapters
#-a 0x20 - may be different subtitke streams, usually starts from 20 and growing 20....29, 2a, 2b ...
#-c 255,0,255,255 - you have to experiment with this. Last number means background. 255 - white, 0- black
tccat -i $DVD_PATH -T 1,-1 | tcextract -x ps1 -t vob -a 0x20 | subtitle2pgm  -c 255,0,255,255 -o f0ff
pgm2txt f0ff
for x in *txt; do aspell -c "$x"; done
srttool -s -w -i f0ff.srtx -o  f0ff.srt

split  -f f0ff -b %04d.pgm.txt  scarface.txt  '/----------/' {991}

####################################
# How to rip subtitles from dvd
###################################

DVD_PATH='~/Wideo/Scarface_dvd/Scarface 1932/'
TITLE=2
NR=20;  #number of subtitle chanel in hex
NR_MAX=29

while [[ NR -lt $NR_MAX ]];
do 
	mkdir napisy_$NR;
	cd napisy_$NR; 
	rm *; 
	#usually you need to tune 255,0,0,255 value
	tccat  -d 3 -i $DVD_PATH   -T$TITLE,-1 | tcextract -x ps1 -t vob -a 0x$NR | subtitle2pgm  -c 255,0,0,255 -o f0ff;
	cd ..; 
	let NR+=1; 
done

# now we have to manually change ready catalogue names from napisy_20 to napisy_en_20

# and next convert to png
find napisy_??_2* -name \*.pgm -exec convert \-verbose \{\} \{\}.png \; -exec rm -v \{\} \;

#OCR with tesseract
find -type f -name \*png -exec convert \{\} \{\}.tif \; -exec tesseract \{\}.tif \{\} -l eng \;

#rename and create srt file
rename.ul .pgm.png. .pgm. *pgm.png.txt
srttool -s -w -i f0ff.srtx -o  f0ff.srt
