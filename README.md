# rogui

A GUI for plotting data written in TKinter

plotgui contains the basic structure, while rotationgui is a basic implementation for looking for periodic variability. The GUIs are intended to be extended by the users to suit their specific purpose. 

Example lightcurves are contained in the examples folder. To run, start ipython and:
%run runro example.cat

Use the quit button to quit the GUI. 

Known bugs:
Using other matplotlib windows while running the GUI does not work.
Not tested with python3

Dependencies for base code:
numpy, scipy, Tkinter, matplotlib, threading, pickle

Examples also requite astropy