#!/usr/bin/perl -w 

use strict;
use warnings;
use utf8;

use Encode;
while(<STDIN>){
	
	my $utf8 =  Encode::decode('utf-8', $_);
	$utf8 =~ tr/żółćęśląźń/zolceslazn/;
	$utf8 =~ tr/ŻÓŁĆĘŚLĄŹŃ/ZOLCESLAZN/;

	print $utf8;
}

