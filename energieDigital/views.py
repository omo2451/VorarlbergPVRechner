# -*- coding: utf-8 -*-
from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
import matplotlib.pyplot as plt
from django.conf import settings
import pandas as pd
import datetime as dt

# Parameterdefinition
al = 0.2
aziFl = 0           # [grad] Richtung Süden ausgerichtet 
neig = 10           # [grad]

# Funktionsdefinition für den Sonnenstand
cos  = lambda arg : np.cos(np.deg2rad(arg))
sin  = lambda arg : np.sin(np.deg2rad(arg))
acos = lambda arg : np.rad2deg(np.arccos(arg))
asin = lambda arg : np.rad2deg(np.arcsin(arg))

# Daten importieren 
# T2m: 2-m air temperature (degree Celsius)
# RH: relative humidity (%)
# G(h): Global irradiance on the horizontal plane (W/m2)
# Gb(n): Beam/direct irradiance on a plane always normal to sun rays (W/m2)
# Gd(h): Diffuse irradiance on the horizontal plane (W/m2)
# IR(h): Surface infrared (thermal) irradiance on a horizontal plane (W/m2)
# WS10m: 10-m total wind speed (m/s)
# WD10m: 10-m wind direction (0 = N, 90 = E) (degree)
# SP: Surface (air) pressure (Pa)

fileendung = '.csv'
ort_CSV = 'Alberschwende'
print(settings.STATIC_ROOT)
filename =settings.STATIC_ROOT+ort_CSV+fileendung
print(filename)

def testfunction(request):
    if request.POST: # wenn "Enter" gedrückt wird
        dic = request.POST # Werte von Page übernehmen
        print('mal sehen was das ist: ' + str(dic))
        ort_CSV = dic['nCycleHin']
    else:
        ort_CSV = 'error'   
    filename =settings.STATIC_ROOT+ort_CSV+fileendung
    print(filename)   
    df_LnB = pd.read_csv(filename, delimiter=':', header = 0,nrows = 2)
    bg=df_LnB.iloc[0,0]   
    lg=df_LnB.iloc[0,1]       
    print (bg)
    print (lg)
    df = pd.read_csv(filename, delimiter=',', header = 2, index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y%m%d:%H%M') 

    hGlo  = df['Gb(n)'].values    # [W/m2] 
    hDif  = df['Gd(h)'].values    # [W/m2]
    hDir = hGlo - hDif # [W/m2]
    
    tutc  = df.index    # Zeit als "string" in UTC
    lfStd = np.zeros(tutc.size)
    for t in range(tutc.size):
        noDay = (tutc[t] - dt.datetime(tutc[0].year, 1, 1, 0)).days # berechnet laufender Tag im Jahr
        noHou = tutc[t].hour + (tutc[t].minute)/60 + (tutc[t].second)/3600   # [h] berechnet laufende Stunde im Tag
        lfStd[t] = noDay*24 + noHou
			
    deltaT = lfStd[1] - lfStd[0] # [h]
    #Sonnenstand
    omega = 15*np.mod(lfStd,24) + float(lg) -180 # [grad] Stundenwinkel
    dekl = 23.45*cos(360/8760*(lfStd-173*24)) # [grad] Deklination
    h = asin(sin(dekl)*sin(float(bg)) + cos(dekl)*cos(float(bg))*cos(omega))
    azi = acos((sin(h)*sin(float(bg)) - sin(dekl))/(cos(h)*cos(float(bg))))*np.sign(omega)
    # Leere Winkel-Arrays erstellen
    neigArray = np.linspace(0,90,90)            # Neigung (Werte über ein bestimmtes Intervall)
    aziArray = np.array(range(-90, 91))         # Azimut (Winkel von 90 bis -90)

    pPVTot = np.zeros((neigArray.size, aziArray.size))  # Jährliche 
    for n in range(neigArray.size):
      #  print('Status: ' + str(n) + ' von ' + str(neigArray.size))
        for i, aziFl in enumerate(aziArray):
            neig = neigArray[n]

				# 3K-Modell
            cosTheta = cos(neig)*sin(h) + sin(neig)*cos(h)*cos(azi - aziFl)
            hDirFl = (hDir/np.maximum(sin(h),sin(5)))*cosTheta
            hDifFl = hDif*0.5*(1+cos(neig))
            hAlbFl = hGlo*al*(1-cos(neig))
            hFl = hDirFl + hDifFl + hAlbFl # [W/m2]        
            pPVTot[n, i] = (np.sum(hFl)*deltaT/1000)       # [kWh] Jahresenergie  
    
    filenameCreated = settings.STATIC_ROOT + 'sinus.jpg'
    CS = plt.contour(aziArray, neigArray, pPVTot, 20)
    #x = np.linspace(0,2*3.14*nCycle,1000)
    #y = np.sin(x)
    #plt.plot(x,y)
    plt.clabel(CS, inline=1, fontsize=10, fmt='%.f')
    plt.xlabel('Azimut [grad]')
    plt.ylabel('Neigung [grad]')
    plt.title ('Jahresertrag [kWh]')
    plt.grid()
    plt.savefig(filenameCreated)
    plt.clf() # Figure-Objekt schliessen
    
    return render(request, 'test.html', {'nCycleZurueck': ort_CSV})
    

def chart(request):
    if request.POST: # wenn "Enter" gedrückt wird
        dic = request.POST # Werte von Page übernehmen
        print('mal sehen was das ist: ' + str(dic))
        
        ort_CSV = dic['nCycleHin']
        print(ort_CSV)
    else:
        ort_CSV = 'error'   
    filename =settings.STATIC_ROOT+ort_CSV+fileendung
    print(filename)   
    df_LnB = pd.read_csv(filename, delimiter=':', header = 0,nrows = 2)
    bg=df_LnB.iloc[0,0]   
    lg=df_LnB.iloc[0,1]       
    print (bg)
    print (lg)
    df = pd.read_csv(filename, delimiter=',', header = 2, index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y%m%d:%H%M') 

    hGlo  = df['Gb(n)'].values    # [W/m2] 
    hDif  = df['Gd(h)'].values    # [W/m2]
    hDir = hGlo - hDif # [W/m2]
    
    tutc  = df.index    # Zeit als "string" in UTC
    lfStd = np.zeros(tutc.size)
    for t in range(tutc.size):
        noDay = (tutc[t] - dt.datetime(tutc[0].year, 1, 1, 0)).days # berechnet laufender Tag im Jahr
        noHou = tutc[t].hour + (tutc[t].minute)/60 + (tutc[t].second)/3600   # [h] berechnet laufende Stunde im Tag
        lfStd[t] = noDay*24 + noHou
			
    deltaT = lfStd[1] - lfStd[0] # [h]
    #Sonnenstand
    omega = 15*np.mod(lfStd,24) + float(lg) -180 # [grad] Stundenwinkel
    dekl = 23.45*cos(360/8760*(lfStd-173*24)) # [grad] Deklination
    h = asin(sin(dekl)*sin(float(bg)) + cos(dekl)*cos(float(bg))*cos(omega))
    azi = acos((sin(h)*sin(float(bg)) - sin(dekl))/(cos(h)*cos(float(bg))))*np.sign(omega)
    # Leere Winkel-Arrays erstellen
    neigArray = np.linspace(0,90,90)            # Neigung (Werte über ein bestimmtes Intervall)
    aziArray = np.array(range(-90, 91))         # Azimut (Winkel von 90 bis -90)

    pPVTot = np.zeros((neigArray.size, aziArray.size))  # Jährliche 
    for n in range(neigArray.size):
      #  print('Status: ' + str(n) + ' von ' + str(neigArray.size))
        for i, aziFl in enumerate(aziArray):
            neig = neigArray[n]

				# 3K-Modell
            cosTheta = cos(neig)*sin(h) + sin(neig)*cos(h)*cos(azi - aziFl)
            hDirFl = (hDir/np.maximum(sin(h),sin(5)))*cosTheta
            hDifFl = hDif*0.5*(1+cos(neig))
            hAlbFl = hGlo*al*(1-cos(neig))
            hFl = hDirFl + hDifFl + hAlbFl # [W/m2]        
            pPVTot[n, i] = (np.sum(hFl)*deltaT/1000)       # [kWh] Jahresenergie  
    
    filenameCreated = settings.STATIC_ROOT + 'sinus.jpg'
    CS = plt.contour(aziArray, neigArray, pPVTot, 20)
    #x = np.linspace(0,2*3.14*nCycle,1000)
    #y = np.sin(x)
    #plt.plot(x,y)
    plt.clabel(CS, inline=1, fontsize=10, fmt='%.f')
    plt.xlabel('Azimut [grad]')
    plt.ylabel('Neigung [grad]')
    plt.title ('Jahresertrag [kWh] in ' +ort_CSV )
    plt.grid()
    plt.savefig(filenameCreated)
    plt.clf() # Figure-Objekt schliessen
    #x = np.linspace(0,100,100)
    #y = np.sin(x/100*2*3.1415*nCycle)    
    #p1 = figure(plot_width=460, plot_height=200)
    #p1.line(x, y)
    #p1.toolbar.logo = None    

    #script, div = components(p1)
    #chart = script + div
        
    #return render(request, 'home.html', {'nCycle': nCycle, 'chart': chart})
    return render(request, 'home.html', {'nCycleZurueck': ort_CSV})

