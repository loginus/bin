#! /usr/bin/python

komunikat='Wpisz kolejn ocen (lub x, aby zakoczy wpisywanie):'
l=0
ile=0
liczba=raw_input(komunikat);
while liczba!='x':
	if liczba!='':
		l=l+int(liczba);
		ile=ile+1
	liczba=raw_input(komunikat);

print 'wpisanych jest',ile,'ocen'
print 'ich rednia to',l/ile
							 
