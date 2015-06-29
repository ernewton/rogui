# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 09:27:35 2015

@author: enewton
"""
from plotgui import PlotGui
from colors_rgba import colors_rgba

import os
import sys
if sys.version_info[0] < 3:
    from Tkinter import *
else:
    from tkinter import *
import tkMessageBox
import tkFont  
import tkFileDialog

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# main GUI
class RGui(PlotGui):
    
    def __init__(self,root,
                 figfunc,   ## function for the plotting
                 readfunc,  ## function for reading in data
                 fitfunc,
                 filelist,  ## list of files
                 verbose=1):

        
        self.readfunc = readfunc
        self.fitfunc = fitfunc
        self.figfunc = figfunc
                         
        # make figure
        self.fig = plt.figure()
        self.fig.set_size_inches(13,7.5)

        # read in the data and plot it
        self.data = self.readfunc(filelist[0])
        self.subplots = self.figfunc(self.data, self.fig) 

        # make the GUI
        PlotGui.__init__(self, root, self.fig)

        # lower frames for period fitting options
        lower = Frame(root, borderwidth=1)
        lower.pack()
        lower_left = Frame(lower)
        lower_left.pack(side = LEFT, fill = BOTH, padx= 20, pady = 10)
        lower_right = Frame(lower)
        lower_right.pack(side = RIGHT, fill = BOTH, padx = 20, pady = 10)  

        # text box for period entry
        self.period_entry=StringVar()
        entry = Entry(lower_left, textvariable=self.period_entry)
        entry.pack(side=RIGHT)
        Label(lower_left, text='New period to plot:', font=self.smallfont).pack(side= RIGHT)

        # rephase the model using the current period and replot
        rephase = Button(lower_right, text='Phase fold and plot model', command=self.update_model, font=self.bigfont)
        rephase.pack(side = LEFT)

        # lower frames for period fitting options
        lower2 = Frame(root, borderwidth=1)
        lower2.pack()
        lower_left2 = Frame(lower2)
        lower_left2.pack(side = LEFT, fill = BOTH, padx= 20, pady = 10)
        lower_right2 = Frame(lower2)
        lower_right2.pack(side = RIGHT, fill = BOTH, padx = 20, pady = 10)  

        # min and max period to fit
        Label(lower_left2,text='P(min) -> P(max):   ', font=self.smallfont).pack(pady=self.padding, side=LEFT)
        self.pmin=StringVar()
        entry = Entry(lower_left2, textvariable=self.pmin, width=10)
        self.pmin.set(0.1)
        entry.pack(side=LEFT)

        self.pmax=StringVar()
        entry = Entry(lower_left2, textvariable=self.pmax, width=10)
        self.pmax.set(1000.)
        entry.pack(side=RIGHT)
        
        # refit using the current options and plot the results
        refit = Button(lower_right2, text='Re-fit and plot periodogram', command=self.refit, font=self.bigfont)
        refit.pack(side = LEFT)
 

        ######
        # This changes the overall state
        state_frame = Frame(root)
        state_frame.pack(padx=self.padding, pady=self.padding)
        next_lc = Button(state_frame, text='Next Light Curve', font=self.bigfont, command= lambda: self.step_lc(direction=1))
        next_lc.pack(side = RIGHT)
        prev_lc = Button(state_frame, text='Previous Light Curve', font=self.bigfont, command= lambda: self.step_lc(direction=-1))
        prev_lc.pack(side = RIGHT)

        ######
        # SAVE OPTIONS

        save_frame = Frame(root)
        save_frame.pack()

        # directory for output files
        self.file_dir_button = Button(state_frame, text='Directory', command= self.choose_file_dir, font=self.smallfont, width=10)
        self.file_dir_button.pack(side = LEFT, fill=BOTH, pady=self.padding)
        self.file_dir_value = StringVar()
        self.file_dir_value.set(os.path.dirname(os.getcwd()))
        Entry(state_frame,textvariable=self.file_dir_value,font=self.smallfont).pack(side=LEFT, pady=self.padding, padx=self.padding)

        # period rating label and drop down menu        
        Label(save_frame, text='   Period Rating', font=self.bigfont).pack(side=LEFT, pady=self.padding)
        ratings = ['yes', 'yesbut','possibly','unknown','weird']
        self.rating = StringVar()
        self.rating.set('unknown')
        option = OptionMenu(save_frame, self.rating, *ratings)
        option.pack(side=LEFT, padx=self.padding, pady=self.padding)

        # period rating label and drop down menu        
        Label(save_frame, text='   Evolving?', font=self.bigfont).pack(side=LEFT, pady=self.padding)
        evolutions = ['strongly', 'some evidence','not clearly']
        self.evolution = StringVar()
        self.evolution.set('not clearly')
        option = OptionMenu(save_frame, self.evolution, *evolutions)
        option.pack(side=LEFT, padx=self.padding, pady=self.padding)
        
        # comment box
        Label(save_frame, text='   Comment', font=self.bigfont).pack(side=LEFT, pady=self.padding)
        self.comment = StringVar()
        entry = Entry(save_frame, textvariable = self.comment, font=self.bigfont)
        entry.pack(side=LEFT, padx=self.padding, pady=self.padding)

        # SAVE!
        Button(save_frame, text='Save', font=self.bigfont, command=self.save_lc, width=10).pack(side=RIGHT, padx=2*self.padding, pady=self.padding)

    # fit the data using supplied function
    def refit(self, vbest=None):
        
        try:
            pmin = float(self.pmin.get())
            pmax = float(self.pmax.get())
        except:
            print "Invalid pmin or pmax, using defaults."
            pmin = 0.1
            pmax = 1000

        f, p, a = self.fitfunc(self.data, pmin=pmin, pmax=pmax, vbest=vbest)
        self.frequency = f
        self.phase = p
        self.amplitude = a
        self.update_model(do_fit=False)
    
    # update the model using the supplied period
    def update_model(self, do_fit=True):

        try:
            if do_fit:
                self.refit(vbest=1./float(self.period_entry.get()))
            self.fig.clf() ## clear the figure
            self.subplots = self.figfunc(self.data, self.fig, 
                                    frequency = self.frequency,
                                    phase = self.phase,
                                    amplitude = self.amplitude)
            self.redraw()
        except:
            print "failed to updated model given supplied period."

    # save user data on the light curve
    def save_lc(self):
        pass
    
    # next light curve
    def step_lc(self):
        pass



######
# fit data
######
import scipy.signal as signal
def fit_period(lc_data,
               pmin = 0.1, pmax=1000.,
               vbest = None):

    lc = lc_data ## place holder for more complicated stuff

    # test frequencies
    freqs = np.linspace(pmin, pmax, 1000)

    # get the best fit
    scaled_mags = (lc['flux']-lc['flux'].mean())/lc['flux'].std()
    periodogram = signal.lombscargle(np.array(lc['time']).astype('float64'), np.array(scaled_mags).astype('float64'), freqs)

    phase = 0.
    amplitude = 0.01
    frequency = freqs[np.argmax(periodogram)]
    
    if vbest is not None:
        frequency = vbest
    
    print "Best fit:", frequency
    return frequency, phase, amplitude


######
# read in data
######
def read_text(myfile):
    lc = np.genfromtxt(myfile,
                       usecols = (0,1,2),
                       dtype={"names": ("time", "flux", "e_flux"),
                              "formats": ("f8", "f4", "f4")})
        
    return pd.DataFrame(lc)

######
# plots
######
import math
def rotation_plot(lc_data, 
                  fig, 
                  plot_binned=False,
                  plot_model=True,
                  frequency=1., phase=0., amplitude=0.01
                  ):  

    nrows = 3
    if type(lc_data) is list:
        ncols = len(lc_data) 
    else:
        ncols = 1
        
    # now plot everything
    for i in range(0,ncols):
        
        if type(lc_data) is list:
            lc = lc_data[i]
        else:
            lc = lc_data
            
        c = colors_rgba(lc['e_flux'])         
        # raw light curve: flux v. data number
        dat = fig.add_subplot(nrows,ncols,1+i)  
        plt.scatter(np.arange(len(lc['flux'])), lc['flux'], color=c)
        
        # raw light curve: flux v. time
        raw = fig.add_subplot(nrows,ncols,1+ncols+i, sharey=dat)
        plt.scatter(lc['time'], lc['flux'], color=c)
        if plot_model:
            axrange=np.linspace(np.min(lc['time']),np.max(lc['time']),1000)
            y = amplitude*np.sin(2*math.pi*(axrange)*frequency + phase)
            plt.plot(axrange,y,c='k')
    
        # phased light curve: flux v. phase
        phased = fig.add_subplot(nrows,ncols,1+2*ncols+i, sharey=dat)
        time_folded = np.fmod((lc['time'])*frequency, 1.0)
        plt.scatter(time_folded, lc['flux'], color=c)
        if plot_model:
            axrange=np.linspace(0,1,1000)
            y = amplitude*np.sin(2*math.pi*axrange+phase)
            plt.plot(axrange,y,c='k') 

        if plot_binned:
            step = 0.1
            for j in range(0,int(1./step)):
                stamp = step/2. + step*j
                diff = np.absolute(time_folded-stamp)
                use = lc['flux'][diff < step]
                tuse = time_folded[diff < step]
                phased.scatter(np.nanmean(tuse),np.nanmean(use),marker='s',s=70,c='k')
                phased.errorbar(np.nanmean(tuse),np.nanmean(use), yerr=np.nanstd(use)/np.sqrt(len(use)-1.),
                                color='k', capthick=1)
    
        # save the subplots!
        if i == 0:
            my_subplots = [dat,raw,phased]
        else:
            my_subplots.append([dat,raw,phased])
            # supress plot labels for all but left-most column
            raw.yaxis.set_visible(False)
            phased.yaxis.set_visible(False)
            dat.yaxis.set_visible(False)
    
    plt.gca().invert_yaxis()
    plt.tight_layout() # too much white space! Narrow all the gaps
    plt.subplots_adjust(wspace=0.07) # even more
    
    return my_subplots


# files to include are the arguments
try:
    filelist = ['']*len(sys.argv[1:])
    for i, arg in enumerate(sys.argv[1:]):
        print "Reading file ", arg
        filelist[i] = arg
except:
    raise("No files provided")

    
# run the GUI
root = Tk() # create a root window
pg = RGui(root, rotation_plot, read_text, fit_period, filelist)
root.mainloop()
