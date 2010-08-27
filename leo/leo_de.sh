#!/bin/bash
INPUT=$1
curl "http://dict.leo.org/ende?lp=ende&lang=de&searchLoc=0&cmpType=relaxed&sectHdr=on&spellToler=on&chinese=both&pinyin=diacritic&search=$INPUT&relink=on" | html2text | sed -e "s/_/ /g" |  grep --colour -i $INPUT
