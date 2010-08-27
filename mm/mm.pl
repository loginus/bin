#!/usr/bin/perl -w
#Author Jahagirdar Vijayvithal S
#email: Jahagirdar_vs (at) yahoo.com
#Description: see http://ed-i.netfirms.com/utils/index.html
#Licensing: Opensource(Attribution Assurance Licenses http://www.opensource.org/licenses/attribution.php)
#Date Created: Thu May 05 12:32:26 2005 2005
#------------------------------------------------------------------------------
use strict;
use XML::Simple;
$|++;
my $xmlfile=$ARGV[0];
my $xs1=XML::Simple->new();
my $config;
my $cfgfile=$ENV{HOME}."/.mm2latexrc";
if (-e $cfgfile ){
	my $xs2=XML::Simple->new();
	$config=  $xs2->XMLin($cfgfile);
}
print STDERR "presentation title?";
$config->{title}{value}=<STDIN>;
my $doc = $xs1->XMLin($xmlfile);
my $hier=0;
my %hsh;
my $type="";
print "% printdoc\n";
bmertemplate($doc->{node}{TEXT});
printdoc($doc,$hier,0);
print "% content\n";
foreach (sort keys %hsh){
	if (/^[0-9]+-[0-9]+$/){
		if( exists $hsh{$_}{'title'}){
			print "\\part{$hsh{$_}{'title'}}\n";
		}
	}
	if (/^[0-9]+-[0-9]+-[0-9]+-[0-9]+$/){
		if( exists $hsh{$_}{'title'}){
			print "\\subsection{$hsh{$_}{'title'}}\n";
		}
	}
	if (/^[0-9]+-[0-9]+-[0-9]+$/){
		if( exists $hsh{$_}{'title'}){
			print "\\section{$hsh{$_}{'title'}}\n";
		}
	}
	#print "$_ the dollor\n";
	if( exists $hsh{$_}{'data'}){
		my $lines= $hsh{$_}{'data'};
		my $num_lines=split /\\item/,$lines;
		my $num_words=split/./,$lines;
		if ($num_lines>5 or $num_words>((47*5)+100)){
			print "\\begin{frame}[allowframebreaks]";
		}else{
			print "\\begin{frame}";
		}
		print <<EOF;
		\\frametitle{$hsh{$_}{'title'}}
		\\begin{itemize}
EOF

		if( exists $hsh{$_}{'target'}){
			print "\\hypertarget{$hsh{$_}{'target'}}\n";
		}
		print <<EOF
		$hsh{$_}{'data'}
		\\end{itemize}
		\\end{frame}
EOF

	}
}
print "\\end{document}";

sub printdoc{
	my ($doc,$hier,$count)=@_;
	if (ref($doc) eq "HASH"){
		printhash($doc,$hier,$count);
	}
	elsif (ref($doc) eq "ARRAY"){
		printarray($doc,$hier,$count);
	}
	elsif (ref($doc) eq "REF"){
		printref($doc,$hier,$count);
	}
}
sub printhash{
	my ($doc,$hier,$count)=@_;
	foreach my $key (keys (%{$doc})){
		if($key eq "node"){
			if (ref($doc->{$key})){
				printdoc($doc->{$key},"$hier-$count",$count);
			}
		}
		elsif ($key eq "TEXT"){
			if (exists $doc->{node}){
			$hsh{$hier}{'data'}.= texClean("\\item $doc->{$key} \\hyperlink{$hier-$count}{\\beamergotobutton{Details}}\n");
				$hsh{"$hier-$count"}{'title'}= texClean($doc->{TEXT});
				$hsh{"$hier-$count"}{'target'}="$hier-$count";
			}
			else {

				$hsh{$hier}{'data'}.= texClean("\\item $doc->{$key}\n");
				return;
			}

		}
	}
}


sub printarray{
	my ($doc,$hier,$count)=@_;
	$count=0;
	foreach my $key (@{$doc}){
		if (ref($key)){
			$count++;
			printdoc($key,$hier,$count);
		}
	}
}

sub bmertemplate{
	my $title=shift;
print <<EOF;
\\documentclass{beamer}
\\mode<presentation>
{
  \\usetheme{Szeged}
  \\setbeamercovered{transparent}
}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{polski}

\\usepackage{times}
\\title[$title] % (optional, use only with long paper titles)
{$config->{title}{value}}
\\author % (optional, use only with lots of authors)
{$config->{name}{value} \\\\$config->{email}{value}}
\\institute % (optional, but mostly needed)
{$config->{department}{value}\\\\$config->{org}{value}}

\\date % (optional)
{\\today }
\\subject{Talks}
% If you have a file called "university-logo-filename.xxx", where xxx
% is a graphic format that can be processed by latex or pdflatex,
% resp., then you can add a logo as follows:

% \\pgfdeclareimage[height=0.5cm]{university-logo}{university-logo-filename}
% \\logo{\\pgfuseimage{university-logo}}
\\AtBeginSubsection[]
{
  \\begin{frame}<beamer>
    \\frametitle{Outline}
    \\tableofcontents[currentsection,currentsubsection]
  \\end{frame}
}
% If you wish to uncover everything in a step-wise fashion, uncomment
% the following command: 

%\\beamerdefaultoverlayspecification{<+->}
\\begin{document}
\\begin{frame}
  \\titlepage
\\end{frame}

\\begin{frame}
  \\frametitle{Outline}
  \\tableofcontents
  % You might wish to add the option [pausesections]
\\end{frame}
EOF
}
sub texClean{
	my $string=shift;
$string=~s/&#xa;/\\ \\/g;
$string=~s/&/\\&/g;
$string=~s/_/\\_/g;
return $string;
}
