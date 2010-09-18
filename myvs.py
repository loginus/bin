#!/usr/bin/env python
#
# Author: Alessandro Arrichiello
#
# Script based on youtube-dl.py by Ricardo Garcia Gonzalez
#	
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import sys
import optparse
import httplib
import urllib2
import re
import string
import os
import time
import netrc
import getpass

# First off, check Python and refuse to run
if sys.hexversion < 0x020400f0:
	sys.exit('Error: Python 2.4 or later needed to run the program')

# Global constants
const_video_url_str = 'http://www.youtube.com/watch?v=%s'
const_video_url_re = re.compile(r'(?:http://)?(?:www\d*\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?v=)([^&]+).*')
const_login_url_str = 'http://www.youtube.com/login?next=/watch%%3Fv%%3D%s'
const_login_post_str = 'current_form=loginForm&next=%%2Fwatch%%3Fv%%3D%s&username=%s&password=%s&action_login=Log+In'
const_age_url_str = 'http://www.youtube.com/verify_age?next_url=/watch%%3Fv%%3D%s'
const_age_post_str = 'next_url=%%2Fwatch%%3Fv%%3D%s&action_confirm=Confirm'
const_video_url_params_re = re.compile(r'player2\.swf\?([^"]+)"', re.M)
const_video_url_real_str = 'http://www.youtube.com/get_video?%s'
const_video_title_re = re.compile(r'<title>YouTube - ([^<]*)</title>', re.M | re.I)
const_1k = 1024
const_initial_block_size = 10 * const_1k

# Print error message, followed by standard advice information, and then exit
def error_advice_exit(error_text):
	sys.stderr.write('Error: %s.\n' % error_text)
	sys.stderr.write('Try again several times. It may be a temporal problem.\n')
	sys.stderr.write('Other typical problems:\n\n')
	sys.stderr.write('\tVideo no longer exists.\n')
	sys.stderr.write('\tVideo requires age confirmation but you did not provide an account.\n')
	sys.stderr.write('\tYou provided the account data, but it is not valid.\n')
	sys.stderr.write('\tThe connection was cut suddenly for some reason.\n')
	sys.stderr.write('\tYouTube changed their system, and the program no longer works.\n')
	sys.stderr.write('\nTry to confirm you are able to view the video using a web browser.\n')
	sys.stderr.write('Use the same video URL and account information, if needed, with this program.\n')
	sys.stderr.write('When using a proxy, make sure http_proxy has http://host:port format.\n')
	sys.stderr.write('Try again several times and contact me if the problem persists.\n')
	sys.exit('\n')

# Wrapper to create custom requests with typical headers
def request_create(url, data=None):
	retval = urllib2.Request(url)
	if data is not None:
		retval.add_data(data)
	# Try to mimic Firefox, at least a little bit
	retval.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0')
	retval.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	retval.add_header('Accept', 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5')
	retval.add_header('Accept-Language', 'en-us,en;q=0.5')
	return retval

# Perform a request, process headers and return response
def perform_request(url, data=None):
	request = request_create(url, data)
	response = urllib2.urlopen(request)
	return response

# Convert bytes to KiB
def to_k(bytes):
	global const_1k
	return bytes / const_1k

# Conditional print
def cond_print(str):
	global cmdl_opts
	if not cmdl_opts.quiet:
		sys.stdout.write(str)
		sys.stdout.flush()

# Title string normalization
def title_string_norm(title):
	title = ''.join((x in string.ascii_letters or x in string.digits) and x or ' ' for x in title)
	title = '_'.join(title.split())
	title = title.lower()
	return title

# Generic download step
def download_step(return_data_flag, step_title, step_error, url, post_data=None):
	try:
		cond_print('%s... ' % step_title)
		data = perform_request(url, post_data).read()
		cond_print('done.\n')
		if return_data_flag:
			return data
		return None

	except (urllib2.URLError, ValueError, httplib.HTTPException, TypeError):
		cond_print('failed.\n')
		error_advice_exit(step_error)

	except KeyboardInterrupt:
		sys.exit('\n')

# Generic extract step
def extract_step(step_title, step_error, regexp, data):
	try:
		cond_print('%s... ' % step_title)
		match = regexp.search(data)
		
		if match is None:
			cond_print('failed.\n')
			error_advice_exit(step_error)
		
		extracted_data = match.group(1)
		cond_print('done.\n')
		return extracted_data
	
	except KeyboardInterrupt:
		sys.exit('\n')

# Calculate new block size based on previous block size
def new_block_size(before, after, bytes):
	new_min = max(bytes / 2, 1)
	new_max = max(bytes * 2, 1)
	dif = after - before
	if dif < 0.0001:
		return new_max
	rate = int(bytes / dif)
	if rate > new_max:
		return new_max
	if rate < new_min:
		return new_min
	return rate

# Create the command line options parser and parse command line
cmdl_usage = 'usage: myvs [options] video_url'
cmdl_version = '0.1'
cmdl_parser = optparse.OptionParser(usage=cmdl_usage, version=cmdl_version, conflict_handler='resolve')
cmdl_parser.add_option('-h', '--help', action='help', help='print this help text and exit')
cmdl_parser.add_option('-v', '--version', action='version', help='print program version and exit')
cmdl_parser.add_option('-u', '--username', dest='username', metavar='USERNAME', help='account username')
cmdl_parser.add_option('-p', '--password', dest='password', metavar='PASSWORD', help='account password')
cmdl_parser.add_option('-o', '--output', dest='outfile', metavar='FILE', help='output video file name')
cmdl_parser.add_option('-q', '--quiet', action='store_true', dest='quiet', help='activates quiet mode') 
cmdl_parser.add_option('-s', '--stream', action='store_true', dest='stream', help='do not download video, but stream directly by mplayer')
cmdl_parser.add_option('-C', '--cache', action='store_true', dest='cache', help='set a cache of 300k, for slow connection')
cmdl_parser.add_option('-c', '--cycle', action='store_true', dest='cycle', help='cycle 20 times while youtube redirect to vo.llnwd.net (that streams .flv)')
cmdl_parser.add_option('-t', '--title', action='store_true', dest='use_title', help='use title in file name')
cmdl_parser.add_option('-n', '--netrc', action='store_true', dest='use_netrc', help='use .netrc authentication data')
cmdl_parser.add_option('-O', '--streamonly', action='store_true', dest='streamonly', help='Force the script to stream only, if it doesnt find a valid stream server simply quit')

(cmdl_opts, cmdl_args) = cmdl_parser.parse_args()

# Get video URL
if len(cmdl_args) != 1:
	cmdl_parser.print_help()
	sys.exit('\n')
video_url_cmdl = cmdl_args[0]

# Verify video URL format and convert to "standard" format
video_url_mo = const_video_url_re.match(video_url_cmdl)
if video_url_mo is None:
	sys.exit('Error: URL does not seem to be a youtube video URL. If it is, report a bug.')
video_url_id = video_url_mo.group(1)
video_url = const_video_url_str % video_url_id

# Check conflicting options
if cmdl_opts.outfile is not None and cmdl_opts.stream:
	sys.stderr.write('Warning: video file name given but will not be used.\n')

if cmdl_opts.outfile is not None and cmdl_opts.use_title:
	sys.exit('Error: using the video title conflicts with using a given file name.')

if cmdl_opts.use_netrc and cmdl_opts.password is not None:
	sys.exit('Error: using netrc conflicts with giving command line password.')

# Incorrect option formatting
if cmdl_opts.username is None and cmdl_opts.password is not None:
	sys.exit('Error: password give but username is missing.')

# Get account information if any
account_username = None
account_password = None

if cmdl_opts.use_netrc:
	try:
		info = netrc.netrc().authenticators('youtube')
		if info is None:
			sys.exit('Error: no authenticators for machine youtube.')
		netrc_username = info[0]
		netrc_password = info[2]
	except IOError:
		sys.exit('Error: unable to read .netrc file.')
	except netrc.NetrcParseError:
		sys.exit('Error: unable to parse .netrc file.')

if cmdl_opts.password is not None:
	account_username = cmdl_opts.username
	account_password = cmdl_opts.password
else:
	if cmdl_opts.username is not None and cmdl_opts.use_netrc:
		if cmdl_opts.username != netrc_username:
			sys.exit('Error: conflicting username from .netrc and command line options.')
		account_username = cmdl_opts.username
		account_password = netrc_password
	elif cmdl_opts.username is not None:
		account_username = cmdl_opts.username
		account_password = getpass.getpass('Type YouTube password and press return: ')
	elif cmdl_opts.use_netrc:
		if len(netrc_username) == 0:
			sys.exit('Error: empty username in .netrc file.')
		account_username = netrc_username
		account_password = netrc_password

# Get output file name 
if cmdl_opts.outfile is None:
	video_filename = '%s.flv' % video_url_id
else:
	video_filename = cmdl_opts.outfile

# Check name
if not video_filename.lower().endswith('.flv'):
	sys.stderr.write('Warning: video file name does not end in .flv\n')

# Test writable file
if not cmdl_opts.stream:
	try:
		disk_test = open(video_filename, 'wb')
		disk_test.close()

	except (OSError, IOError):
		sys.exit('Error: unable to open %s for writing.' % video_filename)

# Install cookie and proxy handlers
urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler()))
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor()))

# Log in and confirm age if needed
if account_username is not None:
	url = const_login_url_str % video_url_id
	post = const_login_post_str % (video_url_id, account_username, account_password)
	download_step(False, 'Logging in', 'unable to log in', url, post)

	url = const_age_url_str % video_url_i
	post = const_age_post_str % video_url_id
	download_step(False, 'Confirming age', 'unable to confirm age', url, post)

# Retrieve video webpage
video_webpage = download_step(True, 'Retrieving video webpage', 'unable to retrieve video webpage', video_url)

# Extract video title if needed
if cmdl_opts.use_title:
	video_title = extract_step('Extracting video title', 'unable to extract video title', const_video_title_re, video_webpage)

# Extract needed video URL parameters
video_url_params = extract_step('Extracting video URL parameters', 'unable to extract URL parameters', const_video_url_params_re, video_webpage)
video_url_real = const_video_url_real_str % video_url_params

# Retrieve video data
try:
	if cmdl_opts.cycle:
		#print video_url_real;
		video_data = perform_request(video_url_real)
		if "vo.llnwd.net" not in video_data.geturl():
			x=0
			from time import sleep
			while "vo.llnwd.net" not in video_data.geturl() and x<=20:
				urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler()))
				urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor()))

				video_webpage = download_step(True, '', 'unable to retrieve video webpage', video_url)
				video_url_params = extract_step('Cycling to find vo.llnwd.net URL..', 'unable to extract URL parameters', const_video_url_params_re, video_webpage)
				video_url_real = const_video_url_real_str % video_url_params
				#print video_url_real;
				video_data = perform_request(video_url_real)
				x +=1
				sleep(2)
			if cmdl_opts.streamonly and "vo.llnwd.net" not in video_data.geturl():
				print "No valid stream server found, option streamonly activated, exiting.."
				sys.exit()
				
	else:
		video_data = perform_request(video_url_real)	
	cond_print('Video data found at %s\n' % video_data.geturl())
	death=0
	if "vo.llnwd.net" not in video_data.geturl():
		death=1
	# stream mode
	if cmdl_opts.stream and (death!=1):
		if cmdl_opts.cache:
			command = 'mplayer -vc ffflv -ac mp3 -cache 300 -prefer-ipv4 ' + str(video_data.geturl()) + ' >> ~/.myvs.log'		
		else:
			command = 'mplayer -vc ffflv -ac mp3 -nocache -prefer-ipv4 ' + str(video_data.geturl()) + ' >> ~/.myvs.log'
		print 'Running:', command
		os.system(command)
		sys.exit()
	else:
		print 'Warning! This webserver not support flv streaming, so I must download the video..'
		print 'Download will start soon, please be patient..'
	video_file = open(video_filename, 'wb')
	try:
		video_len_str = '%sk' % to_k(long(video_data.info()['Content-length']))
	except KeyError:
		video_len_str = '(unknown)'

	byte_counter = 0
	block_size = const_initial_block_size
	while True:
		cond_print('\rRetrieving video data... %sk of %s ' % (to_k(byte_counter), video_len_str))
		before = time.time()
		video_block = video_data.read(block_size)
		after = time.time()
		dl_bytes = len(video_block)
		if dl_bytes == 0:
			break
		byte_counter += dl_bytes
		video_file.write(video_block)
		block_size = new_block_size(before, after, dl_bytes)

	video_file.close()
	cond_print('done.\n')
	cond_print('Video data saved to %s\n' % video_filename)
	command = 'mplayer -vc ffflv -ac mp3 -nocache -prefer-ipv4 ' + str(video_filename) + ' >> ~/.myvs.log'
	print 'Running:', command
	os.system(command)
except (urllib2.URLError, ValueError, httplib.HTTPException, TypeError):
	cond_print('failed.\n')
	error_advice_exit('unable to download video data')

except KeyboardInterrupt:
	sys.exit('\n')

# Rename video file if needed
if cmdl_opts.use_title:
	try:
		final_filename = '%s-%s.flv' % (title_string_norm(video_title), video_url_id)
		os.rename(video_filename, final_filename)
		cond_print('Video file renamed to %s\n' % final_filename)
	
	except OSError:
		sys.stderr.write('Warning: unable to rename file.\n')

	except KeyboardInterrupt:
		sys.exit('\n')

# Finish
sys.exit()
