#!/bin/sh

echo Kompresuje pliki przy pomocy 7zip
echo Użycie:
echo 7z.sh archiwum plik1 plik2 plik3 ....

ARCHIVE=$1".tar.7z";

shift

tar cf - $@ | 7za a -si $ARCHIVE -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on
