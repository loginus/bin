#!/usr/bin/python

A=[15, 22, 23, 23, 24, 24];
B=[6, 2, 3, 4, 5, 6];

print ':::: Kiedy przypadnie wielkanoc ::::';

rok=input('Podaj rok ');
if rok<=1582:
	stalaA=A[0];
	stalaB=B[0];
elif rok<=1699:
	stalaA=A[1];
	stalaB=B[1];
elif rok<=1899:
	stalaA=A[(rok-1500)/100];
	stalaB=B[(rok-1500)/100];
elif rok<=2099:
	stalaA=A[4];
	stalaB=B[4];
else:
	stalaA=A[5];
	stalaB=B[5];
	
resztaA=rok%19;
resztaB=rok%4;
resztaC=rok%7;
resztaD=(resztaA*19+stalaA)%30;
resztaE=(2*resztaB+4*resztaC+6*resztaD+stalaB)%7;
data=22+resztaD+resztaE;
miesiac='marca';
if data>31:
	data-=31;
	miesiac='kwietnia';
	if data>=25:
		data-=7;
print data, miesiac;
