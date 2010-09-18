#!/usr/bin/perl -w

use strict;

my $curr;

while(<>){
	if($curr=/title=(.+)/){
		my $title=$1;
	}
	
	elsif($curr=/artist=(.+)/){
		my $artist=$1;
	}
	
	elsif($curr=/album=(.+)/){
		my $album=$1;
	}
	
	elsif($curr=/year=(.+)/){
		my $year=$1;
	}
	
	elsif($curr=/comment=(.+)/){
		my $comment=$1;
	}
	
	elsif(/--list--/){
		last;
	}
}

chomp(my @utwory=`ls /tmp/muzyka/WLADZIO/wladzio1/*ogg`);

my $i=0;

while(<>){
	my @utwor=split(/--/);
	my $numer=$utwor[0];
	my $tytul=$utwor[1];
	$tytul=~s/\s+$//;
	my $nowa_nazwa= $tytul;
	$nowa_nazwa=~s/ /_/g;
	$nowa_nazwa="/tmp/muzyka/WLADZIO/wladzio1/".$nowa_nazwa.".ogg";
	print "Tworzê: $nowa_nazwa \n";
	my $artysta=$utwor[2];
	$artysta=~s/^\s+//;
	my $wynik=`vorbiscomment -a -t "ARTIST=$artysta" -t "TITLE=$tytul" -t "genre=¦cie¿ka filmowa" -t "date=2001" -t "tracknumber=$numer" -t "ALBUM=The Lord of the Rings - Fellowship of the Ring" $utwory[$i++] $nowa_nazwa`;
#	print $utwory[$i++];
}
