#!/usr/bin/python
"""Bitrate calculator

Calculates video bitrate on the basis of media length and audio bitrate

Usage: python brcalc.py options

Options:
  -a ..., --audiobr=...	media audio bitrate
  -f ..., --file=...	audio bitrate and media length automatically detected from OGG file
  -l ..., --length=...	media length
  -h, 	--help		show this help

Examples:
  brcalc.py -a 100 -l 2823
  brcalc.py -f music.ogg
"""

import sys
from optparse import OptionParser
import subprocess

def usage():
	print __doc__

def main():
	size = 700*1024
	audioBr = None
	length = None
	
	usage = "usage: %prog (-f FILENAME | -l LENGTH -a AUDIOBITRATE)"
    	parser = OptionParser(usage)
  	parser.add_option("-f", "--file", action="store", type="string", dest="filename", help="read length and bitrate from OGG FILE")
	parser.add_option("-l", "--length",action="store", type="int", dest="length", help="file length in seconds")
	parser.add_option("-a", "--audiobr", action="store", type="int",dest="audioBr", help="audiobitrate in kb/s")

	(options, args) = parser.parse_args()
	if options.filename:
		audioBr, length = fromFile(options.filename)
	if options.length:
		length = options.length
	if options.audioBr:
		audioBr = options.audioBr/8.0
		
	if ((audioBr is not None) and (length is not None)):
		bitrate = (size - (audioBr * length )) / length
		print round(bitrate*8)
	else:
		usage()


def fromFile(filename):
	myprocess = subprocess.Popen(['ogginfo',filename],stdout=subprocess.PIPE)
	(sout,serr) = myprocess.communicate()
	trackinfo = {}
	for line in sout.split('\n'):
		for item in ("playback length","average bitrate"):
			if line.strip().lower().startswith(item+":"):
				trackinfo[item] = line.strip()[len(item+":"):].replace(":"," ")
				if item == "average bitrate":
					trackinfo[item]=parseBitrate(trackinfo[item])
				elif item == "playback length":
					trackinfo[item]=parseLength(trackinfo[item])
	print trackinfo
	return trackinfo['average bitrate'], trackinfo['playback length']

def parseBitrate(br):
	bitrate=br.strip().split(' ')[0].replace(',','.')
	return float(bitrate)/8

def parseLength(len):
	times = len.strip().split()
	length=0
	for time in times:
		if time.endswith('m'):
			length+=int(time.replace('m',''))*60
		if time.endswith('s'):
			length+=float(time.replace('s',''))
	return length


if __name__ == "__main__":
	main()

