#for x in *rar ;
#do		
	x=$1;
	echo $x ||exit
	 katalog=$PWD;
	 cd /tmp/paczki
	 unrar x $katalog/"$x" ||exit
	# unzip $katalog/"$x" ||exit
	#tar -xvjf $katalog/"$x" ||exit
	#rozmiar pliku po rozpakowaniu
	y=$(du -sc /tmp/paczki/* |awk '{if ($2~/razem/) print $1}'); 
	if [[ $y -gt 10000 ]]
	then
		slownik="8m"
	else
		slownik="16m"
	fi
	echo $y
	echo "Wybieram Slownik $slownik"
	
	7z a -t7z -m0=lzma -mx=9 -mfb=128 -md=$slownik -ms=on /tmp/wyniki/"$x".7z *   ||exit
	rar a -m5 -mdG -rr1% -s -r /tmp/wyniki/"$x".rar * ||exit
	zip -9r /tmp/wyniki/"$x".zip * ||exit
	tar -cvf /tmp/wyniki/"$x".tar * ||exit
	bzip2 -v9k /tmp/wyniki/"$x".tar ||exit
#	bzz -e4096 /tmp/wyniki/"$x".tar /tmp/wyniki/"$x".tar.bzz ||exit
	gzip -9v /tmp/wyniki/"$x".tar ||exit
	najlepszy=$(ls -1rS /tmp/wyniki |sed -e "2,\$d")
	printf "\n Najlepszy wynik ma: $najlepszy \n"
	
	7z t "/tmp/wyniki/$najlepszy" || unrar t "/tmp/wyniki/$najlepszy" || gunzip -vt  "/tmp/wyniki/$najlepszy" || exit
	mv "/tmp/wyniki/$najlepszy" "$katalog" || exit
	rm /tmp/wyniki/*
	rm -r *
	cd -
#done
