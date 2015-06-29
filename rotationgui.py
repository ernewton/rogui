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
                 filelist,  ## list of files
                 verbose=1):

        # read in the data, which is a dictionary
        self.data = readfunc(filelist[0])
                         
        # make figure
        self.fig = plt.figure()
        self.fig.set_size_inches(13,7.5)
        self.subplots = figfunc(self.data, self.fig) 

        PlotGui.__init__(self, root, self.fig)

        # lower frames for period fitting options
        lower = Frame(root, borderwidth=1)
        lower.pack()
        lower_moreleft = Frame(lower)
        lower_moreleft.pack(side = LEFT, fill = BOTH, padx= 20, pady = 10)
        lower_left = Frame(lower)
        lower_left.pack(side = LEFT, fill = BOTH, padx= 20, pady = 10)
#        lower_middle = Frame(lower)
#        lower_middle.pack(side = LEFT, fill = BOTH, padx= 20, pady = 10)
        lower_right = Frame(lower)
        lower_right.pack(side = RIGHT, fill = BOTH, padx = 20, pady = 10)  


        ######
        # LOWER MIDDLE

        # text box for period entry
        self.period_entry=StringVar()
        entry = Entry(lower_left, textvariable=self.period_entry)
        entry.pack(side=RIGHT)
        Label(lower_left, text='New period to plot:', font=self.smallfont).pack(side= RIGHT)

        # rephase the model using the current period and replot
        rephase = Button(lower_right, text='Phase fold and plot model', command=self.update_model, font=self.bigfont)
        rephase.pack(side = LEFT)


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

            
    def refit(self):
        pass
    
    def update_model(self):
        pass

    def save_lc(self):
        pass
    
    def step_lc(self):
        pass


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
                  fit_dict=None,
                  plot_binned=False,
                  plot_model=False,
                  ):  

    nrows = 3
    if type(lc_data) is list:
        ncols = len(lc_data) 
    else:
        ncols = 1
        
    # now plot everything
    for i in range(0,ncols):
        if fit_dict is not None:
            phase = fit_dict['phase']
            period = 1./fit_dict['frequency']
            amplitude = fit_dict['amplitude']
            print "read fit from dictionary"
        else:
            period = 10.
            phase = 0.
            amplitude = 0.01
        
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
            y = amplitude*np.sin(2*math.pi*(axrange)/period + phase)
            plt.plot(axrange,y,c='k')
    
        # phased light curve: flux v. phase
        phased = fig.add_subplot(nrows,ncols,1+2*ncols+i, sharey=dat)
        time_folded = np.fmod((lc['time'])/period, 1.0)
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
pg = RGui(root, rotation_plot, read_text, filelist)
root.mainloop()
