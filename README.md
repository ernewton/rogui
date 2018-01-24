# rogui

This code provides a framework for exploring astronomical data sets, specifically lightcurves, in the form of a Tkinter GUI. The GUIs are intended to be extended by users to suit their specific purpose. 

## Getting started

### Installing

Clone or download from [https://github.com/ernewton/rogui](https://github.com/ernewton/rogui). Add code location to your path.

### Overview

`plotgui` contains the basic structure, while `rotationgui` is a basic implementation for looking for periodic variability. Two examples are provided. **example** contains lightcurves with white noise and injected sinusoids (created with `create_random.py`). **epic201577109** contains real lightcurves from K2 of an M dwarf star (stars, actually: there are two rotation periods present in the dataset, suggesting binarity). These were downloaded from MAST Jan 17 2018.

### To run

To run the example code, start an ipython session and type:

```%run runro example/example.cat```

or

```%run runk2 epic201577109/201577109.cat```

Use the quit button to quit the GUI. 

### Prerequisites

`numpy`, `scipy`, `Tkinter`, `matplotlib`, `threading`, `pickle`

Examples also require `astropy`

### Known bugs

Using other matplotlib windows while running the GUI does not work.
Not tested with python 3

## License

Copyright 2018 Elisabeth R. Newton. Licensed under the terms of the MIT License (see LICENSE).
