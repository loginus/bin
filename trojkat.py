#!/usr/bin/python

a=input('Prosze podac bok a=');
b=input('Prosze podac bok b=');
c=input('Prosze podac bok c=');

if a>=b and a>=c:
	wynik=	a**2==b**2 + c**2
elif b>=a and b>=c:
	wynik=	b**2==a**2 + c**2
elif c>=a and c>=b:
	wynik=	c**2==a**2 + b**2
	
if wynik:
	tekst= '';
else:
	tekst='nie';

print 'ten trojkat',tekst, 'jest prostokatny'
