#!/bin/sh

echo Kompresuje pliki przy pomocy 7zip
echo Użycie:
echo 7z.sh archiwum plik1 plik2 plik3 ....
echo Archiwa są automatycznie dzielone na bloki po 1GB

ARCHIVE=$1".tar.7z";

shift

tar cf - $@ | 7za a -si $ARCHIVE -t7z -m0=lzma -mx=9 -mfb=128 -md=64m -ms=on -v1g
par2create  -n1 -r5 -u -v $ARCHIVE".par" $ARCHIVE.[0-9][0-9][0-9]
