# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:05:19 2019

@author: mark
"""
import datetime as dt


dateiname = 'myFirstHTML.html'
f = open(dateiname,'r')
inhalt = f.read()
f.close()

tnow = dt.datetime.now()

start = inhalt.find('{% ')
ende  = inhalt.find(' %}')

# Auslesen der "alten" Textstelle, sodass wir dieses später ersetzten können
oldText = ''
for i in range(start+3,ende): # +3 wegen dem Startzeichen "{% "
    oldText = oldText + inhalt[i]

neuerInhalt =inhalt.replace(oldText, str(tnow))

f = open(dateiname,'w')
f.write(neuerInhalt)
f.close()
