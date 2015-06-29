# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 10:38:10 2015

@author: enewton
"""

import matplotlib as mpl
import numpy as np

#####   
# get RGB-alpha colors for light curve based on day (color), flux error (opacity)
def colors_rgba(err, 
                cmap='nipy_spectral',
                single_color=(0.54,0,0,1)):

    # get color map
    try:
        ccmap = mpl.cm.get_cmap(name=cmap) # get color map
    except:
        ccmap = mpl.cm.get_cmap() # get color map
    ccmap._init()
    rgba =  ccmap._lut # RGB-alpha array
    
    # assign colors to data points
    ncol = rgba.size/4 # number of colors (four elements per color)

    colors = np.arange(0,len(err))*(ncol-1)/len(err) # stretch to color range
    colors_rgba=rgba[colors]
    
    if cmap == 'None':
        for i in range(colors_rgba.shape[0]):
            colors_rgba[i]=single_color
        
    # assign transparency to data points based on flux error
    interval = 0.95
    left = sorted(err)[int(round((1.0-interval)*len(err)))]
    right = sorted(err)[min(len(err)-1,int(round(interval)*len(err)))]

    minalpha=0.075
    maxalpha=0.6
    alphas = maxalpha-(err-left)/(right-left)*(maxalpha-minalpha) # goes from 0.1 to 0.8
    alphas[alphas<minalpha]=minalpha
    alphas[alphas>maxalpha]=maxalpha
    colors_rgba[:,-1]=alphas
    
    return colors_rgba
