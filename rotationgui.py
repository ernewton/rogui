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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

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
        self.filelist = filelist
                         
        # make figure
        self.fig = plt.figure()
        self.fig.set_size_inches(13,7.5)

        # read in the data and plot it
        self.star = 'target'
        self.current = 0
        self.data = self.readfunc(self.filelist[self.current])
        #self.refit()

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
        rephase = Button(lower_right, text='Phase fold', command=self.update_model, font=self.bigfont)
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
        refit = Button(lower_right2, text='Re-fit', command=self.refit, font=self.bigfont)
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


        self.refit()
        
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

        if True:
            if do_fit:
                self.refit(vbest=1./float(self.period_entry.get()))
            self.fig.clf() ## clear the figure
            self.subplots = self.figfunc(self.data, self.fig, 
                                    frequency = self.frequency,
                                    phase = self.phase,
                                    amplitude = self.amplitude)
            self.redraw()
        else:
            print "failed to updated model given supplied period."

    # save user data on the light curve
    def save_lc(self):
        myfile = self.dir_value.get() + '/' + self.star + '.pkl'
        data = {'pmin': self.pmin.get(),
                'pmax': self.pmax.get(),
                'frequency': self.frequency,
                'amplitude': self.amplitude,
                'phase': self.phase,
                'rating': self.rating.get(),
                'evolution':self.evolution.get(),
                'comment': self.comment.get()
                }

        if os.path.isfile(myfile):
            message = "The file %s already exists! Do you want to overwrite?" % myfile
            if tkMessageBox.askyesno("Plotting GUI",message):
                output = open(myfile, 'wb')               
                pickle.dump(data, output) 
                output.close()
                if self.verbose > 0: print "Saved file."
            else:
                if self.verbose > 0: print "File not saved."
        else:
            output = open(myfile, 'wb')                 
            pickle.dump(data, output) 
            output.close()
            if self.verbose > 0: print "Saved file."
    
    # next light curve
    def step_lc(self, direction=1):
        # only step if you haven't reached the end or the beginning
        if (self.current != 0 and direction < 0) or (self.current != len(self.filelist)-1 and direction > 0):
            self.current += direction*1
            self.data = self.readfunc(self.filelist[self.current])
            self.refit()
        else:
            message = "You've reached the end of the list! Staying on current light curve."
            tkMessageBox.showwarning("LC Step", message) 



