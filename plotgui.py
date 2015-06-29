# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 15:04:07 2014

@author: enewton
"""

import os
import sys
if sys.version_info[0] < 3:
    from Tkinter import *
else:
    from tkinter import *
import tkMessageBox
import tkFont
import tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import pandas as pd


######
# A plotting GUI
######

class PlotGui():
 
    def __init__(self,root,fig,verbose=0):
        # to do: dynamically choose whether y range is equal-sided
        self.verbose = verbose
        self.fig = fig
        
        # basic settings
        root.title("Plotting GUI ") # title the window
        self.bigfont = tkFont.Font(family="Times", size=16) # title font
        self.smallfont = tkFont.Font(family="Times", size=12) # text font
        self.padding = 10 # amount of padding

        # upper GUI: plot and y limit bar
        upper = Frame()
        upper.pack(side=TOP)

        # for the plot created above
        plot_frame = Frame(upper)
        plot_frame.pack(side=RIGHT, padx=self.padding, pady=self.padding)
        
        # draw it
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side = RIGHT)
        self.canvas.mpl_connect('button_press_event', self.clicked)
        # bind mouse click event to canvas
        #self.canvas.bind("<Button-1>", self.clicked)

        # left side
        side_frame = Frame(upper)
        side_frame.pack(side = LEFT, padx=self.padding/2.)

 
        # redraw button
        redraw = Button(side_frame, text='Redraw', font=self.bigfont, command=self.redraw)
        redraw.pack(side = TOP, pady=self.padding, fill=BOTH)

        # one y limit scale that effects all subplots
        self.subplots = self.fig.axes[:]
        ylim_scale = self.setup_lim_scales(side_frame,
                                            subplots=self.subplots,
                                            scale_range=[0,self.subplots[0].get_ylim()[1]*10.])

        ylim_scale.set(self.subplots[0].get_ylim()[1]) # set to current upper limit
        ylim_scale.pack()

        # zoom
        self.zooming = False
        self.leftzoom = None
        self.rightzoom = None
        label = Button(side_frame,text='Zoom', font=self.bigfont, command=self.set_zoom)
        label.pack(pady=self.padding, fill=BOTH)

        # reset button
        reset = Button(side_frame, text='Reset', font=self.bigfont, command=self.reset)
        reset.pack(side = TOP, pady=self.padding, fill=BOTH)
 
        # save figure button
 
        save_fig = Button(side_frame, text='Save Figure', font=self.bigfont, command=self.save_fig)
        save_fig.pack(side = TOP, pady=self.padding, padx=self.padding)

        self.dir_button = Button(side_frame, text='Directory', command= self.choose_dir)
        self.dir_button.pack(fill=BOTH, pady=self.padding/2., padx=self.padding)
        self.dir_value = StringVar()
        self.dir_value.set(os.path.dirname(os.getcwd()))
        Entry(side_frame,textvariable=self.dir_value,font=self.smallfont).pack(padx=self.padding)
  
#        self.file_button = Button(side_frame, text='File Name', command= self.choose_file)
#        self.file_button.pack(fill=BOTH, pady=self.padding, padx=self.padding)
#        self.file_value = StringVar(os.path.dirname(os.path.realpath(__file__)))
        self.file_value = StringVar()
        self.file_value.set('figure.ps')
        Entry(side_frame,textvariable=self.file_value,font=self.smallfont).pack(pady=self.padding)

  
    ###### 
    # scaling provided subplots to values 
    def scale_plots(self,subplots,values={}):

        try: # if this doesn't work... ## should do this more better
            subplots[0]
        except: # fix the most common issue
            subplots = [subplots]
        for i in range(0,len(subplots)):
            low, high = subplots[i].get_ylim()
            left, right = subplots[i].get_xlim()
            if 'low' in values: 
                low = values['low']
            if 'high' in values:
                high = values['high']
            if 'left' in values:
                left = values['left']
            if 'right' in values:
                right = values['right']
            subplots[i].get_ylim()
            subplots[i].set_ylim([low,high])
            subplots[i].set_xlim([left,right])


    ######
    # make a single y limit scale that applies to a group of subplots
    # goes bad if mirror, fixupper and fixlower all False!
    def setup_lim_scales(self, 
                          frame, 
                          subplots,
                          scale_range=np.array([0,1]), 
                          mirror=True, # y axes mirrowed?
                          #fixlower=False,
                          #fixupper=False,
                          varylower=True,
                          varyupper=True,
                          resolution=0.005, 
                          length=250,
                          pack=False, # pack in by default
                          label='',
                          x=FALSE
                         ): 
        print self.subplots
        if x: # x axis scale
            orientation = HORIZONTAL
            low='left'
            high='right'
        else: # y axis scale
            orientation = VERTICAL
            low='low'
            high='high'
        if mirror: # if equal variations centered around zero
            ylim_scales = Scale(frame, font=self.smallfont,
                            from_=scale_range[0], to=scale_range[1], 
                            resolution=resolution,
                            length=length,  
                            orient=orientation, relief=FLAT,
                            command= lambda value: self.scale_plots(subplots,{low:-1*float(value),high:float(value)}))
        else: # for separate scales
            ylim_scales = []
            if varyupper: # if vary upper limit
                ylim_scales.append(Scale(frame, label=label, font=self.smallfont,
                            from_=scale_range[0], to=scale_range[1], 
                            resolution=resolution,
                            length=length,  
                            orient=orientation, relief=FLAT,
                            command= lambda value: self.scale_plots(subplots,{high:float(value)})))
            if varylower: # if vary lower limit
                ylim_scales.append(Scale(frame, label=label, font=self.smallfont,
                            from_=scale_range[0], to=scale_range[1], 
                            resolution=resolution,
                            length=length,  
                            orient=orientation, relief=FLAT,
                            command= lambda value: self.scale_plots(subplots,{low:float(value)})))

        return ylim_scales
 
    # register a click
    def clicked(self, event):
        x, y = event.xdata, event.ydata
        if self.verbose > 1: print "plotgui:clicked: Last point clicked at x=%s y=%s" % (x, y)

        if self.zooming:
            if self.leftzoom is None:
                self.leftzoom = [x,y]
            elif self.rightzoom is None:
                self.rightzoom = [x,y]
            if (self.leftzoom is not None) & (self.rightzoom is not None):
                xlow = self.leftzoom[0]
                xhigh = self.rightzoom[0]
                ylow = self.leftzoom[1]
                yhigh = self.rightzoom[1]
                self.scale_plots(self.subplots, 
                                 values={'left':xlow,'right':xhigh,'low':ylow,'high':yhigh})
                self.zooming = False
                self.leftzoom = None
                self.rightzoom = None
                self.redraw()

        return [x,y]
    
    # pay attention to mouse clicks for zoom
    def set_zoom(self):
        self.zooming = True

    # redraw script
    def redraw(self):
        self.canvas.draw()
       
    def reset(self):
        for ax in self.subplots:
            ax.autoscale()  # auto-scale
            ax.autoscale_view(True,True,True)
        self.canvas.draw()       # re-draw the figure

    # save figure
    def save_fig(self, file_name=None, dir_name=None):
        # make the file name
        if file_name is None:
            file_name = self.file_value.get()
        if dir_name is not None:
            myfile = dir_name + '/' + file_name
        else:
            myfile = file_name
            
        # the file exists!
        if os.path.isfile(myfile):
            message = "The file %s already exists! Do you want to overwrite?" % myfile
            if tkMessageBox.askyesno("Plotting GUI",message):
                self.fig.savefig(myfile)
                
                if self.verbose>0: print "plotgui:save_fig: Saved file. Overwrote ", myfile
            else:
                if self.verbose>0: print "plotgui:save_fig: File not saved. %s already exists." % myfile
        # the file doesn't exist
        else:
            self.fig.savefig(myfile)
            if self.verbose>0: print "plotgui:save_fig: Saved file ", myfile

    # choose a save directory 
    def choose_dir(self):
        dir_name = tkFileDialog.askdirectory()
        self.dir_value.set(str(dir_name) if dir_name else os.path.abspath(os.path.realpath(__file__)))

    # choose dir value for fitting file saves
    def choose_file_dir(self):
        file_dir_name = tkFileDialog.askdirectory()
        self.file_dir_value.set(str(file_dir_name) if file_dir_name else os.path.abspath(os.path.realpath(__file__)))
