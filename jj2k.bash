#!/bin/bash
CLASSPATH=/tmp/kde-wojtek5Erlmq/jj2000-4.1/jj2000-4.1.jar:$CLASSPATH
export CLASSPATH
convert $1 $1.ppm
echo "Converting done"
java JJ2KEncoder -i $1.ppm -o $1.jp2 -rate $2
display $1.ppm  $1.jp2
rm $1.ppm
