#!/bin/bash
INPUT_ENC="utf-8";
OUTPUT_ENC="latin2";
OLD=$1;
NEW=`echo "$OLD" |  iconv -f $INPUT_ENC -t $OUTPUT_ENC` 
NEW_ASCII=`echo   $NEW |  sed -e 'y/Í Û”±°∂¶≥£øØº¨Ê∆Ò—/eEoOaAsSlLzZzZcCnN/'`
echo $NEW;
echo $NEW_ASCII;
mv -iv "$OLD" "$NEW_ASCII"
