#!/bin/bash
#zmienia nazwy podanym plikom ogg na nazwe utworu
for x in $@;
do
	nazwa=$(vorbiscomment -l $x |grep title |sed -e "s/title=//
	s/ /_/g");
	mv $x $nazwa".ogg";
done
