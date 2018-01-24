# rogui

A GUI for examining lightcurve data written in TKinter

`plotgui` contains the basic structure, while `rotationgui` is a basic implementation for looking for periodic variability. The GUIs are intended to be extended by the users to suit their specific purpose. Two examples are provided. *example* contains lightcurves with white noise and injected sinusoids (created with `create_random.py`); *epic201577109* contains real lightcurves from K2 of an M dwarf star (stars, actually: there are two rotation periods present in the dataset, suggesting binarity).

To run, start ipython and:
`%run runro example/example.cat`
or
`%run runk2 epic201577109/201577109.cat`

Use the quit button to quit the GUI. 

Known bugs:
Using other matplotlib windows while running the GUI does not work.
Not tested with python 3

Dependencies for base code:
`numpy`, `scipy`, `Tkinter`, `matplotlib`, `threading`, `pickle`

Examples also require `astropy`