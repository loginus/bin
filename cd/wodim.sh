#!/bin/sh
ISO_IMAGE="$1"
DEVICE=/dev/cdrw3
MAX_SIZE=734000000

echo "MD5 sum counting"
SUMA=`md5sum $ISO_IMAGE | awk '{print $1}'`
echo $SUMA

RESULTS_SIZE=`stat -c %s $ISO_IMAGE`
OVERBURN=""
if [ "$RESULTS_SIZE" -gt $MAX_SIZE ]
then
	echo "Image size ($RESULTS_SIZE) exceeded 700M. Overburn option turned on"
	OVERBURN="-overburn"
fi

wodim -vv $OVERBURN dev=$DEVICE  -eject speed=24 fs=8m -sao -minbuf=95 "$ISO_IMAGE"
eject -t  $DEVICE || read input
SUMA_PO_NAGRANIU=`md5sum $DEVICE | awk '{print $1}'`
echo $SUMA_PO_NAGRANIU
echo $SUMA
if [ "sum${SUMA}" = "sum${SUMA_PO_NAGRANIU}" ] 
then 
	echo "Hurra udało się"; 
	rm "$ISO_IMAGE"
	exit
fi
echo "Sumy kontrolne $SUMA i $SUMA_PO_NAGRANIU różnią się"
