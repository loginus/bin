#!/usr/bin/perl

# kmailpt.pl (c) 2007 J.C. Cardot - jice<at>lea-linux.org
#
# kmailpt takes an email on stdin, performs actions based
# on this mail, then output an email on stdout.
# Without any option, it will remove any file attached.
#
# possible actions are:
# - detach attachments (save and remove from the email)
# - remove all attachments from the email
# - remove the attachment chosen by the user from the email
# - store an email decrypted (gpg)

use Getopt::Long;
use MIME::Parser;
use MIME::WordDecoder;
use File::Copy;
use POSIX qw(strftime);

use vars qw( $PROGRAM $VERSION $COPYLEFT );
$PROGRAM   = "KMail power tools";
$VERSION   = "0.3";
$COPYLEFT  = "(c) 2007 Jean-Christophe Cardot <kmailpt\@cardot.net>\nThis program is distributed under the terms of the GPL licence";
my $title = '"KMail Power Tools v'.$VERSION.' (c) 2007 JCC"';

# options parsing
my $usage = "Usage: kmailpt [action] [options]

kmailpt takes an email on stdin, performs actions based
on this mail, then output the resulting email on stdout.

Actions: (one among these options is mandatory)
        -a       remove all attachments (no user interaction)
        -q       ask which attachment to remove
        -d [dir] detach the attachments (save and remove).
                 When given the optional argument directory,
                 detaches all the attachments to this directory
                 (no user interaction)
        -g       decrypt gpg emails (to store them decrypted)
Options:
        -m       add the detached/removed file md5 to the message
        -s       add the detached/removed file size to the message
        -n       multiline disclaimer
        -p       use gpg-agent (don't ask for gpg passphrase)
        -h       prints this help\n";
sub usage { print STDERR "$PROGRAM $VERSION\n$COPYLEFT\n$usage"; }
our ($opt_a, $opt_q, $opt_d, $opt_m, $opt_s, $opt_n, $opt_g, $opt_p, $opt_h);
# we need to use Getopt::Long because -d has an optional argument
Getopt::Long::Configure('bundling');
unless (GetOptions(
	'a'   => \$opt_a,
	'q'   => \$opt_q,
	'd:s' => \$opt_d,
	'm'   => \$opt_m,
	's'   => \$opt_s,
	'n'   => \$opt_n,
	'g'   => \$opt_g,
	'p'   => \$opt_p,
	'h'   => \$opt_h,)) { usage(); exit 1 };

if ($opt_h) { usage(); exit 0 }

# one of these option is mandatory
if (!$opt_a and !$opt_q and ! defined $opt_d and !$opt_g) { print STDERR 'One option among a, q, d, and g is mandatory'."\n"; usage(); exit 1 }

# separator for the disclaimer
my $sep = $opt_n?"\n* ":', ';
my $sephtml = $opt_n?"<br />\n* ":', ';

my $parser = new MIME::Parser;

# table of attachments
my @attach;

# tables of bodies, sizes, md5sums, destinations
my %bodies;
my %sizes;
my %md5sums;
my %destinations,

# flag: removed attachments?
my $removed = 0;

# destination of saved files (option -d)
my $destdir;

# gpg passphrase
my $passphrase = "";

my $output = $ENV{'HOME'} . '/.kmailpt';

# create output dir if not exist
mkdir $output;
chmod 0700, $output;

# set output dir for temporary files
$parser->output_dir($output);
# Keep parsed message bodies in core (default outputs to disk):
#$parser->output_to_core(1);

# slurp the message
my $OLD_RS = $/;
undef $/;
my $msg = <>;
$/ = $OLD_RS;

sub cleanup { $parser->filer->purge; }

sub exitonerror {
	my $errmsg = shift;
	print STDERR 'kmailpt error: '.$errmsg."\n" if $errmsg;
	print $msg;
	cleanup();
	exit 0;
}

sub remove_requested {
	my $att = shift;
	foreach my $a (@attach) {
		return 1 if $a eq $att;
	}
	0;
}

sub isMultipart {
	my $part = shift; 
	if ( ($part->effective_type eq 'multipart/alternative')
	  or ($part->effective_type eq 'multipart/mixed')
	  or ($part->effective_type eq 'multipart/related')
	  or ($part->effective_type eq 'message/rfc822') ) {
		return 1;
	}
	0;
}

# keep only parts without a filename
sub keep_part {
	my $wd = default MIME::WordDecoder;
	my $part = shift;
	my $filename = $wd->decode($part->head->recommended_filename);
	if ($filename and remove_requested($filename)) {
		$removed = 1;
		return 0;
	}
	1;
}

# and do it recursively
sub keep_parts {
	my $entity = shift;
	my @parts = $entity->parts;
	if (@parts) {
		my @keep = grep { keep_part($_) } @parts;
		$entity->parts(\@keep);
	}
	foreach my $part ($entity->parts) {
		$part = keep_parts($part) if isMultipart($part);
	}
	return $entity;
}

sub get_attachment_name {
	my $wd = default MIME::WordDecoder;
	my $part = shift;
	my $filename = $wd->decode($part->head->recommended_filename);
	if ($filename) {
		#$attach .= ($attach?" ":"") . $filename . " " . $filename . " " . $filename;
		push @attach, $filename;
		$bodies{$filename} = $part->bodyhandle;
		if (($opt_m or $opt_s) and defined($bodies{$filename}->path)) {
			my $fn = $bodies{$filename}->path;
			($sizes{$filename}, $dummy) = split(/\s/, `du -b "$fn"`) if $opt_s;
			($md5sums{$filename}, $dummy) = split(/\s/, `md5sum -b "$fn"`) if $opt_m;
		}
	        else {
			$sizes{$filename} = 'Unknown size';
			$md5sums{$filename} = 'Unknown md5sum';
	        }
	}
}

sub get_attachment_names {
	my $entity = shift;
	my @parts = $entity->parts;
	if (@parts) {
		grep { get_attachment_name($_) } @parts;
	}
	foreach my $part ($entity->parts) {
		get_attachment_names($part) if isMultipart($part);
	}
}

# create the disclaimer
sub create_disclaimer {
	my ($disc, $dischtml, $extra);
	my %extras;
	$disc = `whoami`; $disc =~ s/\n//;
	$disc .= strftime(" (%d/%m/%Y %H:%M:%S)", localtime);
	# additional information about the file (size, md5)
	foreach my $a (@attach) {
		$extra = '';
		$extra .= $sizes{$a}.' bytes' if $opt_s;
		$extra .= ', ' if $opt_m and $opt_s;
		$extra .= 'md5: '.$md5sums{$a} if $opt_m;
		$extra  = ' ('.$extra.')' if $opt_m or $opt_s;
		$extras{$a} = $extra;
	}
	# detach
	if (defined $opt_d) {
		my ($savedto, $savedtohtml);
		foreach my $a (@attach) {
			$savedto .= ($savedto?$sep:'') . 'file://' . $destinations{$a} . $extras{$a};
			$savedtohtml .= ($savedtohtml?$sephtml:'') . "<a href='file://$destinations{$a}'>$a</a>$extras{$a}";
		}
		$disc = $dischtml = 'Attachment'.(@attach>1?'s':'').' saved by '.$disc.' to:'; 
		$disc     .= ($opt_n?$sep:' ').$savedto;
		$dischtml .= ($opt_n?$sephtml:' ').$savedtohtml;
	# remove
	} else {
		my ($removed, $removedhtml); 
		foreach my $a (@attach) {
			$removed .= ($removed?$sep:'') . $a . $extras{$a};
			$removedhtml .= ($removedhtml?$sephtml:'') . $a . $extras{$a};
		}
		$disc = $dischtml = 'Attachment'.(@attach>1?'s':'').' removed by '.$disc.':';
		$disc     .= ($opt_n?$sep:' ').$removed;
		$dischtml .= ($opt_n?$sephtml:' ').$removedhtml;
	}
	$disc     = '['.$disc.']'     if !$opt_n;
	$dischtml = '['.$dischtml.']' if !$opt_n;
	return ($disc, $dischtml);
}

# recursively add the disclaimer
# in text/plain and text/html parts
# FIXME: does not always add the disclaimer to the right part (ex: encapsulated messages)
sub add_disclaimer {
	my ($entity, $disc, $dischtml) = @_;
	foreach my $part ($entity->parts) {
		if (my $body = $part->bodyhandle
		  and (($part->effective_type eq 'text/html') or ($part->effective_type eq 'text/plain'))
		  and ( $part->head->get('Content-Disposition') =~ /^inline/
		       or not $part->head->get('Content-Disposition'))) {
			# read the body text and alter it
			# TODO: add an inline attachment instead?
			#       does it work well with multipart/alternative?
			my $IO = $body->open('r') or exitonerror('Impossible to open mail part');
			my @msg = $IO->getlines;
			my $msg = join('', @msg);
			if ('text/plain' eq $part->effective_type) {
				$msg .= "\n\n$disc\n"; 
			} elsif ('text/html' eq $part->effective_type) {
				$dischtml = "\n<p><span style='font-weight:bold'>$dischtml</span></p>\n";
				if ($msg =~ m|</body>|i) {
					$msg =~ s|</(body)>|$dischtml</$1>|i;
				} elsif ($msg =~ m|</html>|i) {
					$msg =~ s|</(html)>|$dischtml</$1>|i;
				} else {
					$msg .= "$dischtml\n";
				}
			}
			$IO->close or exitonerror('Error when closing mail part');
			# write back the text to the body
			$IO = $body->open('w') or exitonerror('Impossible to open mail part');
			$IO->print($msg);
			$IO->close             or exitonerror('Error when closing mail part');
		} elsif (isMultipart($part)) {
			add_disclaimer($part, $disc, $dischtml);
		}
	}
}

# decrypt a string
sub string_decrypt {
	eval "use GnuPG::Interface";
	exitonerror('string_decrypt: '. $@) if $@;
	exitonerror('string_decrypt: no input') unless my $ciphertext = shift;
	my $gnupg = GnuPG::Interface->new();
	$gnupg->options->meta_interactive(0);
	$gnupg->options->hash_init(armor => 1);
	$gnupg->call('gpg');
	$gnupg->options->push_recipients($key);
	my ($input, $output, $error, $passphrase_fh, $status_fh)
		= (new IO::Handle, new IO::Handle, new IO::Handle, new IO::Handle, new IO::Handle);
	my $handles = GnuPG::Handles->new(
		stdin      => $input,
		stdout     => $output,
		stderr     => $error,
		( $opt_p ?
			() : (passphrase => $passphrase_fh) ),
		status     => $status_fh);
	my $pid = $gnupg->decrypt(handles => $handles);
	exitonerror('NO PASSPHRASE') unless defined $passphrase_fh;
	if (not $opt_p) {
		print $passphrase_fh $passphrase;
		close $passphrase_fh;
	}
	print $input $ciphertext;
	close $input;
	my @plaintext = <$output>;
	close $output;
	my @error_output = <$error>;
	close $error;
	my @status_info = <$status_fh>;
	close $status_fh;
	waitpid $pid, 0;
	($? >> 8, \@plaintext, \@error_output, \@status_info);
}

# encrypt a string for a specified key
sub string_encrypt {
	eval "use GnuPG::Interface";
	exitonerror('string_encrypt: '. $@) if $@;
	my ($plaintext, $key) = @_;
	my $gnupg = GnuPG::Interface->new();
	$gnupg->options->meta_interactive(0);
	$gnupg->options->hash_init(
		armor       => 1,
		default_key => $key);
	$gnupg->call('gpg');
	$gnupg->options->push_recipients($key);
	my ($input, $output, $error)
		= (new IO::Handle, new IO::Handle, new IO::Handle);
	my $handles = GnuPG::Handles->new(
		stdin	=> $input,
		stdout	=> $output,
		stderr	=> $error);
	my $pid = $gnupg->encrypt(handles => $handles);
	print $input $plaintext;
	close $input;
	my @ciphertext = <$output>;
	close $output;
	my @error_output = <$error>;
	close $error;
	waitpid $pid, 0;
	my $exit_value = $? >> 8;
	exitonerror('gpg error: '.$exit_value) if $exit_value;
	return join('', @ciphertext);
}

sub decrypt_email {
	my $entity = shift;

	# ask for passphrase if needed
	if (not $opt_p and not $passphrase) {
		$passphrase = `kdialog --password "This email appears to be encrypted using GPG.\nPlease enter your gpg passphrase:" --title $title`;
		exitonerror() if $? >> 8 != 0; # cancel
	}

	# check that the entity is a well formed gpg encrypted message
	my $armor_message = 0;
	my $ciphertext;
	if ($entity->effective_type eq 'multipart/encrypted') {
		exitonerror('multipart/encrypted messages must have two parts')
			unless ($entity->parts == 2);
		exitonerror('Content-Type not pgp-encrypted')
			unless $entity->parts(0)->effective_type eq 'application/pgp-encrypted';
		$ciphertext = $entity->parts(1)->body_as_string();
		exitonerror('No gpg encrypted message found')
			unless $ciphertext =~ /^-----BEGIN PGP MESSAGE-----/m;
	} elsif ($entity->body_as_string =~ /^-----BEGIN PGP MESSAGE-----/m ) {
		$ciphertext = $entity->body_as_string;
		$armor_message = 1;
	}
	# decrypt the message
	(my $exit_value, my $plaintext, my $error_output, my $status_info)
		= string_decrypt($ciphertext);

	if ($exit_value) {
		`kdialog --error "Sorry but there has been an error while decrypting the email.\nYou probably entered a wrong passphrase." --title $title`;
		exitonerror('gpg error: '.$exit_value.'. Probably wrong passphrase');
	}

	# for armor message (which usually contain no MIME entity)
	# and if the first line seems to be no header, add an empty
	# line at the top, otherwise the first line of a text message
	# will be removed by the parser.
	if ($armor_message and $$plaintext[0] and $$plaintext[0] !~ /^[^\x00-\x1f\x7f-\xff :]+:/) {
		unshift @$plaintext, "\n";
	}

	# get the decrypted entity
	cleanup(); # remove files created for the encrypted entity
	my $entity_clear = $parser->parse_data(join('', @$plaintext));

	# get the key the message was encrypted for
	my $key = "";
	if (join('', @$error_output) =~ /ID\s([0-9A-F]{8}),/i) {
		$key = $1;
	}
	($key, $entity_clear, $plaintext);
}

# add the headers from the original email
sub add_headers {
	my ($entity_src, $entity_dest, $delete_dest_tags) = @_;
	my $tag = '';
	my $tagvalue = '';
	my %deleted;
	if ($delete_dest_tags) {
		foreach my $t (split(/\n/, $entity_dest->head->as_string())) {
			if ($t =~ /^([^\x00-\x1f\x7f-\xff :]+): (.*)$/) {
				$entity_dest->head->delete($1);
				$deleted{$1} = 1;
			}
		}
	}
	foreach my $t (split(/\n/, $entity_src->head->as_string())) {
		if ($t =~ /^([^\x00-\x1f\x7f-\xff :]+): (.*)$/) {
			if ($tag) {
				$entity_dest->head->replace($tag, $tagvalue)
				  if not $entity_dest->head->get($tag) and not $deleted{$tag};
				$tagvalue = '';
			}
			$tag = $1;
			$tagvalue = $2;	
		}
		else {
			$tagvalue .= "\n".$t;
		}
	}
}

# Main processes

sub process_entity {
	my $entity = shift;
	my $original_entity = shift; # optional argument: encrypted entity
	my $plaintext = shift; # optional argument: decrypted text as given by gpg --decrypt

	# manage encrypted emails
	# There are two types of those: multipart/encrypted
	# and text/plain with the mail body as a gpg message (armored)
	if (   ($entity->effective_type eq 'multipart/encrypted')
	    or (  ($entity->effective_type eq 'text/plain')
	      and ($entity->body_as_string =~ /^-----BEGIN PGP MESSAGE-----/m) ) ) {

		(my $key, my $entity_clear, my $plaintext) = decrypt_email($entity);

		# if all the user wants is to decrypt the message, then we must
		# not alter the message content in any way, or the eventual gpg
		# signature might be broken, so we just output the plain text.
		if ($opt_g and not $opt_a and not $opt_q and not defined $opt_d) {
			# add all headers from the original entity except those from the decrypted one
			add_headers($entity, $entity_clear, 1);
			print $entity_clear->head->as_string() . join('', @$plaintext);
		} else {
			$entity_clear = process_entity($entity_clear, $entity, $plaintext);

			if ($opt_g) {
				add_headers($entity, $entity_clear, 0);
				# return the decrypted result
				return $entity_clear;
			} else {
				# encrypt back the message
				# reconstruct the 2 parts:
				# 1. gpg header
				my $head = $entity->header_as_string;
				$head =~ /boundary="([^"]*?)"/;
				my $boundary = $1;
				print $head."\n";
				print '--'.$boundary."\n";
				print 'Content-Type: application/pgp-encrypted'."\n";
				print 'Content-Disposition: attachment'."\n";
				print "\n";
				print 'Version: 1'."\n";
				print '--'.$boundary."\n";

				# 2. gpg encrypted body
				print 'Content-Type: application/octet-stream'."\n";
				print 'Content-Disposition: inline; filename="msg.asc"'."\n";
				print "\n";
				print string_encrypt($entity_clear->as_string, $key);
	
				print '--'.$boundary.'--'."\n";
			}
		}
		cleanup();
		exit 0;
	}

	get_attachment_names($entity) if $opt_a or $opt_q or defined $opt_d;

	if (@attach > 0) {
		# ask the user where to save the attachments (option -d)
		if (defined $opt_d and -d $opt_d) {
			$destdir = $opt_d;
		} elsif (defined $opt_d) {
			$destdir = `kdialog --getexistingdirectory \$HOME --title "Select a directory where to save the attachments"`;
			chomp $destdir;
			# exit if the user pressed cancel
			exitonerror() unless $destdir;
		}
		
		# ask the user for attachments to remove if requested by -q or -d option
		if ($opt_q or (defined $opt_d and not -d $opt_d)) {
			my $cmd = 'kdialog --checklist "Select the attachments to '.($opt_q?'remove':'detach to '.$destdir).'" --title '.$title.' -- ';
			foreach my $a (@attach) { $cmd .= "\"$a\" \"$a\" \"$a\" "; }
			my $ans = `$cmd`; $ans =~ s/\"[^\w\d\-_.]*\n//i; $ans =~ s/^\"//;
			# build the table of requested attachments
			@attach = split('" "', $ans);
		}
	}
	
	if (@attach > 0) {
		# save the attachments if requested (option -d)
		if ($destdir) {
			foreach my $a (@attach) {
				# if the file already exist, then append a dash and a number before the extension
				my $i = 0;
				my ($destination, $fn, $ext);
				if ($a =~ /^(.*?)(\.[\w]{1,4})$/) {
					$fn = $1; $ext = $2;
				} else {
					$fn = $a; $ext = '';
				}
				do {
					$destination = $destdir.'/'.$fn.($i++ > 0?'-'.$i:'').$ext;
				} while ( -e $destination );
				# the %destinations hash is used to build the disclaimer, update it
				$destinations{$a} = $destination;
				# save the file
				if (defined($bodies{$a}->path)) {
					copy($bodies{$a}->path, $destination) or exitonerror('Error when copying file to destination') ;
				}
				else {
					open(destfh, '>'.$destination) or exitonerror('Error when creating destination file') ;
					write(destfh, $bodies{$a}->as_string) or exitonerror('Error when writing to destination file') ;
					close(destfh) or exitonerror('Error when closing destination file') ;
				}
			}
		}
	
		# remove the requested attachments
		$entity = keep_parts($entity);
	
		# if there were no attachments, then do nothing
		if ($removed) {
			# add [Removed attachments: ...] in text/plain & text/html parts
			add_disclaimer($entity, create_disclaimer());
			# output the entity
			return $entity;
		} else {
			exitonerror();
		}
	} else {
		# when we don't modify the email, and the user wants it decrypted,
		# then we have to use the "original" plaintext in order not to break
		# the eventual gpg signature.
		if ($opt_g and $original_entity and $plaintext) {
			add_headers($original_entity, $entity, 1);
			print $entity->head->as_string() . join('', @$plaintext);
			cleanup();
			exit 0;
		}
		exitonerror();
	}
}

sub process_email {
	my $msg = shift;
	# Parse input:
	my $entity = $parser->parse_data($msg) or exitonerror('Error when parsing the email');
	#$entity = $parser->parse(\*STDIN) or exitonerror();
	$entity = process_entity($entity);
	return $entity->as_string();
}

print process_email($msg);
cleanup();