# -*- coding: utf-8 -*-
from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
import matplotlib.pyplot as plt
from django.conf import settings

def testfunction(request):
    if request.POST: # wenn "Enter" gedrückt wird
        dic = request.POST # Werte von Page übernehmen
        print('mal sehen was das ist: ' + str(dic))
        nCycle = int(dic['nCycleHin'])
    else:
        nCycle = int(0)   

    x = np.linspace(0,2*3.14*nCycle,1000)
    y = np.sin(x)
    filename = settings.STATIC_ROOT + 'sinus.jpg'
    
    plt.plot(x,y)
    plt.savefig(filename)
    plt.clf() # Figure-Objekt schliessen
    
    return render(request, 'test.html', {'nCycleZurueck': nCycle})
    

def chart(request):
    if request.POST: # wenn "Enter" gedrückt wird
        dic = request.POST # Werte von Page übernehmen
        print('mal sehen was das ist: ' + str(dic))
        nCycle = int(dic['nCycle'])
    else:
        nCycle = int(1)   

    x = np.linspace(0,100,100)
    y = np.sin(x/100*2*3.1415*nCycle)    
    p1 = figure(plot_width=460, plot_height=200)
    p1.line(x, y)
    p1.toolbar.logo = None    

    script, div = components(p1)
    chart = script + div
        
    return render(request, 'home.html', {'nCycle': nCycle, 'chart': chart})

