
# ------------------------------------------------------------------------------
#
# This file contains the TimeKeeper perl functions
#
# ------------------------------------------------------------------------------
#
# Copyright (C) 2003 Christian Eheim
#
# This file is part of TimeKeeper (timekeeper.sourceforge.net).
#
# TimeKeeper is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# TimeKeeper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TimeKeeper; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# ------------------------------------------------------------------------------
#
# Created on 07/02/2003 by Christian Eheim (scripts@eheim.ch)
#
# LAST MODIFIED:
# $Date: 2003/12/05 22:29:00 $
# $Revision: 1.3 $
# $Author: eheim $
#
# ------------------------------------------------------------------------------

################################################################################
# Functions in this file
#
# Any errors pushed onto the @error array
################################################################################
# Creates a new project
#		sub start_project { my $project = $_[0]; }
# Start the new session for a project
#		sub start_session { my ($project,$date,$time) = @_; }
# Add a new comment to a running session
#		sub add_comment { my ($project,$comment) = @_; }
# End a session - return the session and total time
#		sub end_session { my ($project,$date,$time) = @_; }
# Read the contents of a file - returns an array of line in file
#		sub read_file { my $file = $_[0]; }
# Write an array the a file
#		sub write_file { my ($file, @array) = @_; }
# Creates a new session file
#		sub create_session { my ($project,$date,$time) = @_; }
# Create a new project file
#		sub create_project { my $project = $_[0]; }
# Appends a comment to a file
#		sub append_comment { my ($project,$comment) = @_; }
# gets the date and time - return the date and time
#		sub get_time { } 
# Checks the date and time - returns true or false
#		sub check_datetime { my ($date,$time) = @_; } 
# Checks if the time is valid
#		sub check_time { my $time = $_[0]; } 
# Checks if the date is valid
#		sub check_date { my $date = $_[0]; }
# Check for errors - return whether or not there are errors in @error
#		sub is_error { }
# Delete the file
#		sub delete_file { my $file = shift; }
# Archive a project
#		sub move_file { my $file = shift; }
# Gets the contents of the TimeKeeper directory - returns hash array
#		sub read_dir { my ($dir,$match) = @_; }
# Process the request
#		sub process_request { }
# Delete session from a project file
#		sub remove_sessions { my $project = shift; }
# Delete seesion from a project file
#		sub restore_bak { my $project = shift; }
# Compute the total of two time stamps - return the total
#		sub add_times { my ($t1, $t2) = @_; }

################################################################################
# Creates a new project
################################################################################
sub start_project {
	my $project = $_[0];

	# Make sure the project does not already exist
    if (-f "$timedir/$project.time") {
        push @error, "The project '$project' already exists.";
    }
    # otherwise, create the new project
    else {
		create_project($project);
    }
}

################################################################################
# Start the new session for a project
################################################################################
sub start_session {
	my ($project,$date,$time) = @_;

    # The project must exist
    if (! -e "$timedir/$project.time") {
        push @error, "You must create the project first.";
    }
    # There cannot be a running session
    elsif (-e "$timedir/$project.tmp") {
        push @error, "You must end the last session first.";
    }
    else {
		# Start the session
		$error = create_session($project,$date,$time);
	}
                                                                                
}

################################################################################
# Add a new comment to a running session
################################################################################
sub add_comment {
	my ($project,$comment) = @_;

	# The project must exist
    if (! -e "$timedir/$project.time") {
        push @error,  "You must create the project first.";
    }
    # There must be a running session
    elsif (! -e "$timedir/$project.tmp") {
        push @error,  "You must start the session first.";
    }
    else {
		# Add the comment to the file
		append_comment($project,$comment);
	}
}

################################################################################
# End a session
################################################################################
sub end_session {
	my ($project,$date,$time) = @_;

	# The project must exist
    if (! -e "$timedir/$project.time") {
        push @error,  "You must create the project first.";
    }
    # There must be a running session
    elsif (! -e "$timedir/$project.tmp") {
        push @error,  "You must start the session first.";
    }
	else {

		# If a comment is specified, add it to the session first
		if ($params{'comment'} && $params{'comment'} ne "") {
			add_comment($params{'project'},$params{'comment'});
			if (!is_error()) {
				push @success, "Added the comment to the session for project '$params{'project'}'.";
			}
		}
                                                                                
		#
		# Compute the session time
		#
		my @tmpFile = read_file("$timedir/$project.tmp");
		# Get the start time from the tmp file
		my $sdate = $tmpFile[0];
		chomp($sdate);
		my $stime = $tmpFile[1];
		chomp($stime);
																					
		# Convert the start and end time to seconds
		my $sSec = `date -d "$sdate $stime" +"%s"`;
		chomp($sSec);
		my $eSec = `date -d "$date $time" +"%s"`;
		chomp($eSec);
																					
		# Compute the time difference in seconds
		my $secDiff = $eSec - $sSec;
																					
		# Convert the time difference to hours and minutes
		my $hours = int($secDiff/3600);
		my $mins = ($secDiff- ($hours*3600)) / 60;
		if ($mins < 10) { $mins = "0".$mins; }
																					
		#
		# Compute the total project time
		#
		my @timeFile = read_file("$timedir/$project.time");
																					
		my $total = "$hours:$mins";
																					
		# Add the existing time to the total
		if ($timeFile[$#timeFile] =~ m/^Total Project Time/) {
			my ($text,$ttime) = split(/: /, $timeFile[$#timeFile]);
			$total = add_times($ttime,$total);
		}
																					
		# Add the session to the project
		if (open(FID, ">>$timedir/$project.time")) {
			print FID "\nSession: $sdate $stime - $date $time\n";
			print FID "Session Time: $hours:$mins\n";
			print FID "-"x80;
			print FID "\n";
			for my $ind (3..($#tmpFile-1)) {
				print FID $tmpFile[$ind];
			}
			print FID "-"x80;
			print FID "\n";
			print FID "Total Project Time: $total\n";
			close(FID);

			# Remove the tmp file
			unlink("$timedir/$project.tmp");
		}   
		else {
			push @error, "Can't open $timedir/$project.time";
		}

		return ("$hours:$mins","$total");
	}
}

################################################################################
# Read the contents of a file
################################################################################
sub read_file {
	my $file = $_[0];

    open(FID, "$file") or die "Can't open $file";
    my @tmpFile = <FID>;
    close(FID);

	return @tmpFile;
}

################################################################################
# Write an array the a file
################################################################################
sub write_file {
	my ($file, @array) = @_;
    open(FID, ">$file") or push @error, "Can't write to $file";
		map { print FID $_ } @array;
    close(FID);
}

################################################################################
# Creates a new session file
################################################################################
sub create_session {
	my ($project,$date,$time) = @_;

	# Create the temporary session file
	if (open(FID, ">$timedir/$project.tmp")) {
		print FID "$date\n$time\n\n";
		close(FID);
		chmod(0666,"$timedir/$project.tmp");
	}
	else {
		push @error, "Can't create $timedir/$project.tmp";
	}
}

################################################################################
# Create a new project file
################################################################################
sub create_project {
	my $project = $_[0];

	if (open(FID, ">$timedir/$project.time")) {
		print FID "Created project '$project' on ".scalar(localtime)."\n";
		close(FID);
		chmod(0666,"$timedir/$project.time");
	} else {
		push @error,"Can't create $timedir/$project.time";
	}
}

################################################################################
# Appends a comment to a file
################################################################################
sub append_comment {
	my ($project,$comment) = @_;

	# Add the comment to the file
    if (open(FID, ">>$timedir/$project.tmp")) {
		print FID "$comment\n\n";
		close(FID);
	}
	else {
		push @error, "Can't open $timedir/$project.tmp";
	}
}

################################################################################
# gets the date and time
################################################################################
sub get_time {
	my ($sec,$min,$hr,$day,$month,$year) = localtime();
	$min = "0".$min if ($min<10);
	$hr = "0".$hr if ($hr<10);
	$month++;
	$month = "0".$month if ($month<10);
	$day = "0".$day if ($day<10);
	my $time = "$hr:$min";
	my $date = ($year+1900)."-$month-$day";
	return ($date,$time);
}

################################################################################
# Checks the date and time
################################################################################
sub check_datetime {
	my ($date,$time) = @_;
	check_date($date);
	check_time($time);
	return (is_error()) ? 0 : 1;
}

################################################################################
# Checks if the time is valid
################################################################################
sub check_time {
	my $time = $_[0];
	if ($time !~ m/^[0-9]{2}:[0-9]{2}$/) {
		push @error, "Time '$time' is not valid.";
	}
}

################################################################################
# Checks if the date is valid
################################################################################
sub check_date {
	my $date = $_[0];
	if ($date !~ m/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) {
		push @error, "Date '$date' is not valid.";
	}
}

################################################################################
# Check for errors
################################################################################
sub is_error {
    return (@error > 0) ? 1 : 0;
}

################################################################################
# Delete the file
################################################################################
sub delete_file {
	my $file = shift;
	if (-f "$timedir/$file") {
		unlink("$timedir/$file");
		if (-f "$timedir/$file" ) {
			push @error, "Could not delete file '$timedir/$file'.";
		}
	}
	else { push @error, "File '$timedir/$file' does not exist."; }
}

################################################################################
# Archive a project
################################################################################
sub move_file {
	my $file = shift;
	my $out = "";
	# If the file a a project, move it to the archives
	if ($file =~ /\.time$/) { ($out = $file) =~ s/\.time$/\.archive/; }
	# If the file is an archive, move it to the projects
	elsif ($file =~ /\.archive$/) { ($out = $file) =~ s/\.archive$/\.time/; }
	if (-f "$timedir/$file") {
		if (! rename("$timedir/$file","$timedir/$out") ) {
			push @error, "Could not move file '$timedir/$file'.";
		}
	}
	else { push @error, "File '$timedir/$file' does not exist."; }
}

################################################################################
# Gets the contents of the TimeKeeper directory
################################################################################
sub read_dir {
    my ($dir,$match) = @_;
                                                                                
    opendir(DIR, $dir) or (push @error, "Can't read directory $dir");
    my @files = grep { !(/^\./) && (/\.$match$/) && -f $dir."/".$_ } readdir(DIR);
    closedir(DIR);
                                                                                
    @files = map { s/\.$match$//; $_ } @files;
    @files = sort(@files);
                                                                                
    my %list = map { $files[$_], $_+1 } 0..$#files;
                                                                                
    return %list;
}

################################################################################
# Process the request
################################################################################
sub process_request {
    if ($params{'project'}) {
        #
        # Add a new project
        #
        if ($params{'new'}) {
            if ($params{'project'} ne "" && $params{'project'} !~ /^ *$/) {
                start_project($params{'project'});
                if (!is_error()) {
                    push @success, "Created a new project called '$params{'project'}'";
                }
            }
            else {
                push @error, "'$params{'project'}' is not a valid project name.";
            }
        }
        #
        # Add a comment
        #
        elsif ($params{'add'}) {
            if ($params{'comment'} ne "") {
                add_comment($params{'project'},$params{'comment'});
                if (!is_error()) {
                    push @success, "Added the comment to the session for project '$params{'project'}'.";
                }
            }
            else {
                push @error, "You did not specify a comment.";
                delete $params{'add'};
            }
        }
        #
        # End a session
        #
        elsif ($params{'end'}) {
            if ( check_datetime($params{'date'},$params{'time'}) ) {
                my ($stime,$totime) = end_session($params{'project'},$params{'date'},$params{'time'});
                if (!is_error()) {
                    push @success, "Ended session for '$params{'project'}' at $params{'time'} on $params{'date'}.";
                    push @success, "Session Time: $stime";
                    push @success, "Project Time: $totime";
                }
            }
            else {
                push @error, "You must specify a valid date (yyyy-mm-dd) and time (hh:mm).";
            }
        }
        #
        # Start a new session
        #
        elsif ($params{'start'}) {
            if ( check_datetime($params{'date'},$params{'time'}) ) {
                start_session($params{'project'},$params{'date'},$params{'time'});
                if (!is_error()) {
                    push @success, "Started a new session for '$params{'project'}' at $params{'time'} on $params{'date'}.";
                }
            }
            else {
                push @error, "You must specify a valid date (yyyy-mm-dd) and time (hh:mm).";
            }
        }
        #
        # Delete a project
        #
        elsif ($params{'delete'}) {
            delete_file("$params{'project'}.time");
            if (-f "$timedir/$params{'project'}.tmp") {
                delete_file("$params{'project'}.tmp");
            }
            if (!is_error()) {
                push @success, "Deleted project '$params{'project'}'.";
            }
        }
        #
        # Archive a project
        #
        elsif ($params{'archive'}) {
            if (-f "$timedir/$params{'project'}.tmp") {
                push @error, "You need to end the running session first.";
				return;
			}
            move_file("$params{'project'}.time");
            if (!is_error()) {
                push @success, "Archived project '$params{'project'}'.";
            }
        }
        #
        # Activate an archive
        #
        elsif ($params{'activate'}) {
            move_file("$params{'project'}.archive");
            if (!is_error()) {
                push @success, "Activated project '$params{'project'}'.";
            }
        }
        #
        # Delete a running session
        #
        elsif ($params{'dsess'}) {
            if (-f "$timedir/$params{'project'}.tmp") {
                delete_file("$params{'project'}.tmp");
            }
            if (!is_error()) {
                push @success, "Deleted session for project '$params{'project'}'.";
            }
        }
    }
    elsif ($params{'new'}) {
        push @error, "You must specify a project name.";
    }
}

################################################################################
# Delete seesion from a project file
################################################################################
sub remove_sessions {
	my $project = shift;
    my @lines = ();
	my $file;
    if (-f "$timedir/$project.time") {
        $file = "$timedir/$project.time";
    }
    elsif (-f "$timedir/$project.archive") {
        $file = "$timedir/$project.archive";
    }
    else {
        print "<font color=red>The project '$project' does not exist.</font>";
        exit(0);
    }

	@lines = read_file($file);

	my @out = ();
	my $NOT = 0;
    my $i = 1;
	my $total = "0:0"; # the running total time
	my $stime = "0:0"; # the current session time
	push @out, "$lines[0]";
    for my $ind (2...$#lines) {
        my $line = $lines[$ind];
		chomp($line);
        if ($line =~ m/^Session:/) { 
			if ($params{"proj[$i]"}) { $NOT = 1; }
			push @out, "\n$line\n" unless ($NOT);
			$i++;
		}
        elsif ($line =~ m/^Session Time:/) {
			push @out, $line."\n" unless ($NOT);
			(my $str,$stime) = split(/: /, $line);
		}
        elsif ($line =~ m/^Total Project Time:/) {
			if (!$NOT) {
				$total = add_times($total,$stime);
				push @out, "Total Project Time: $total\n";
			}
			$NOT = 0;
		}
        else {
			if (!$NOT && $line ne "") {
				push @out, $line."\n";
			}
		}
    }

	# Lets make a backup of the project file first
	if ( ! copy($file,"$file.bak") ) {
		push @error, "A backup file of '$file' could not be created.\n";
		push @error, "The sessions have not been deleted.\n";
	}
	else {	
		chmod(0666,"$file.bak");
		# Write the new content of the file
		write_file($file, @out);
	}
}

################################################################################
# Delete seesion from a project file
################################################################################
sub restore_bak {
	my $project = shift;
	my ($file, $bak);
    if (-f "$timedir/$project.time.bak") {
        $file = "$timedir/$project.time";
        $bak = "$timedir/$project.time.bak";
    }
    elsif (-f "$timedir/$project.archive.bak") {
        $file = "$timedir/$project.archive";
        $bak = "$timedir/$project.archive.bak";
    }
    else {
        print "<font color=red>A backup for '$project' does not exist.</font>";
        exit(0);
    }

	if (! copy($bak,$file) ) {
		push @error, "The backup file of '$project' could not be restored.\n";
		push @error, "No changes made.\n";
	}
}

################################################################################
# Compute the total of two time stamps
################################################################################
sub add_times {
	my ($t1, $t2) = @_;
	my ($h1,$m1) = split(/:/, $t1);
	my ($h2,$m2) = split(/:/, $t2);
	# Compute the total minutes
	my $tm = 60 * ( $h1 + $h2 ) + ( $m1 + $m2 );
	my $hours = int($tm/60);
	my $mins  = ($tm - (60*$hours));
	if ($mins < 10) { $mins = "0".$mins; }
	return "$hours:$mins";
}

1;
