#!/usr/bin/python 
#!encoding=iso-8859-2

import datetime, math

urodziny=datetime.date(1988,2,15)
dzis=datetime.date.today()
dni=(dzis-urodziny).days
fizyczna=math.sin(dni/23.0*math.pi*2)
emocjonalna=math.sin(dni/28.0*math.pi*2)
intelektualna=math.sin(dni/33.0*math.pi*2)
print "Dziś jest", dzis
if dzis.month==urodziny.month and dzis.day==urodziny.day:
	print "Dziś są twoje urodziny ;)"
print "Masz", dni, "dni"
print "Forma fizyczna", fizyczna
print "Forma emocjonalna", emocjonalna
print "Forma intelektualna", intelektualna
print " W sumie", (fizyczna+emocjonalna+intelektualna)/3.0
