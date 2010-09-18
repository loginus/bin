#! /usr/bin/python

import math;

print ':::: Rownanie Kwadratowe ::::'

a=input('Prosze poda wspolczynnik a=');
b=input('Prosze poda wspolczynnik b=');
c=input('Prosze poda wspolczynnik c=');
delta=b*b-4*a*c;
if delta == 0:
	print 'x0=' , -b/(2*a)
	
if delta>0:
	print 'x1=',(-b-math.sqrt(delta))/2*a, ' x2=',(-b+math.sqrt(delta))/2*a

if delta<0:
	print "Brak rozwiza rzeczywistych"
