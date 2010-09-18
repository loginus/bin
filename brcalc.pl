#!/usr/bin/perl

use strict;
use Getopt::Std;

my %opts;
getopts('s:l:b:h', \%opts);

if ( $opts{s} ) { our $size = $opts{s}; }
else { our $size = 640; }

if ( $opts{l} ) { our $length = $opts{l}; }
else { our $length = 90; }

if ( $opts{b} ) { our $abr = $opts{b}; }
else { our $abr = 128 }

if ( $opts{h} ) { die "Usage: $0 -s [size in MB] -l [duration in minutes] -b [audio bitrate]\n"; }

my $br = ( $main::size * 1024 * 8 ) / ( $main::length * 60 ) - $main::abr;

print "CD-ROM size: $main::size MB\n";
print "Video duration: $main::length Min\n";
print "Audio bitrate: $main::abr bps\n";
print "----------------------------------\n";
print "Bitrate $br\n";
