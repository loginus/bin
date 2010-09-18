#!/usr/bin/perl -w

use strict;

my $ile=0;
my $razy=1.0013;
while (<>){
	my @linia=split(/[{}]/);
	my $pocz=sprintf ("%d",$linia[1]*$razy+$ile);
	my $koniec=sprintf("%d",$linia[3]*$razy+$ile);
	my $napis=$linia[4];
	print "{$pocz}{$koniec} $napis";
}
