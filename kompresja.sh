#!/bin/bash	

#kompresuje pliki podane jako argumenty na kilka róznych sposobów i wybiera najlepszy (najmniejsze archiwum)
#dostêpne typy archiwów:
# 7z
# Rar
# tar.bz2
# tar.bzz (opcjonalnie - narazie wykomentowane)
# tar.gz
# zip

y=$(du -sc $@ |awk '{if ($2~/razem/) print $1}'); 
if [[ $y -gt 10000 ]]
then
	slownik="8m"
elif  [[ $y -gt 8000 ]]
then
	slownik="16m"
else
	slownik="32m"
fi
echo $y
echo "Wybieram Slownik $slownik"
	
7z a -t7z -m0=lzma -mx=9 -mfb=128 -md=$slownik -ms=on /tmp/wyniki/"$1".7z $@   ||exit
rar a -m5 -mdG -rr1% -s -r /tmp/wyniki/"$1".rar $@ ||exit
zip -9r /tmp/wyniki/"$1".zip $@ ||exit
tar -cvf /tmp/wyniki/"$1".tar $@ ||exit
bzip2 -v9k /tmp/wyniki/"$1".tar ||exit
#	bzz -e4096 /tmp/wyniki/"$1".tar /tmp/wyniki/"$1".tar.bzz ||exit
gzip -9v /tmp/wyniki/"$1".tar ||exit
najlepszy=$(ls -1rS /tmp/wyniki |sed -e "2,\$d")
printf "\n Najlepszy wynik ma: $najlepszy \n"
	
7z t "/tmp/wyniki/$najlepszy" || unrar t "/tmp/wyniki/$najlepszy" || gunzip -vt  "/tmp/wyniki/$najlepszy" || exit
mv "/tmp/wyniki/$najlepszy" ./ || exit
rm /tmp/wyniki/*
