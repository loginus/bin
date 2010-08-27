#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import sgmllib
import codecs


class LeoParser(sgmllib.SGMLParser):
	"A simple parser class."
	def parse(self, s):
        	"Parse the given string 's'."
        	self.feed(s)
        	self.close()

	def __init__(self, verbose=0):
		"Initialise an object, passing 'verbose' to the superclass."
		sgmllib.SGMLParser.__init__(self, verbose)
		self.hyperlinks = []
		self.inside_bold=0
		self.bolds = []

		self.results_table=0
		self.eng=0
		self.english=""
		self.german=""
		self.dictionary={}


	def start_a(self, attributes):
		"Process a hyperlink and its 'attributes'."

		for name, value in attributes:
			if name == "href":
				self.hyperlinks.append(value)


	def get_hyperlinks(self):
		"Return the list of hyperlinks."
		return self.hyperlinks

	def start_b(self, attributes):
		self.inside_bold=1

	def end_b(self):
		self.inside_bold=0

	def handle_data(self,data):
		if self.inside_bold:
			self.bolds.append(data)
		if self.eng==1:
			self.english=self.english+" "+data.strip()
		elif self.eng==3:
			self.german=self.german+" "+data.strip()
	
	def get_bolds(self):
		return self.bolds
	
	def start_table(self, attributes):
		for name, value in attributes:
			if name == "id" and value=="results":
				self.results_table=1
	
#	def end_table(self):
#		self.results_table=0
#		print "END TABLE"
				
	def start_td(self, attributes):
		if self.results_table:
			for name, value in attributes:
				if name=="valign" and value=="middle":
					if self.eng==0:
						self.eng=1
					elif self.eng==2:
						self.eng=3
	
	def end_td(self):
		if self.eng==1:
			self.eng=2
		elif self.eng==3:
			self.eng=0
			self.dictionary[self.english]=self.german
			self.english=""
			self.german=""

	def get_dictionary(self):
		return self.dictionary
	
	def is_results_table(self):
		return self.results_table
					


input_word='hund' 
# Get a file-like object for the Python Web site's home page.
f = urllib.urlopen("http://dict.leo.org/ende?lp=ende&lang=de&searchLoc=0&cmpType=relaxed&sectHdr=on&spellToler=on&chinese=both&pinyin=diacritic&search="+input_word+"&relink=on")
# Read from the object, storing the page's contents in 's'.
s = f.read()
f.close()

myparser = LeoParser()
myparser.parse(s)

bolds = myparser.get_bolds()
if not myparser.is_results_table:
	# Get the hyperlinks.
	print bolds
	hyp=myparser.get_hyperlinks()
	for link in hyp:
		if link.startswith('ende?'):
			print link
else:
	dict = myparser.get_dictionary()
	keys = dict.keys()
	enc = codecs.getencoder('utf-8')
	for key in keys:
		print enc(key+":\t"+dict[key])

