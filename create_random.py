import numpy as np
rand = np.random.RandomState(42)
t = 1000 * rand.rand(300)
y = 0.005*np.sin(2 * np.pi * t/50.) + 0.002 * rand.randn(len(t))
dy = 0.001 + 0.002* rand.rand(len(t))
i = range(300)

from astropy.io import ascii
from astropy.table import Table
data = Table([i, t, y, dy], names=['i', 'time', 'mag', 'error'])
ascii.write(data, 'example/random1.dat')


rand = np.random.RandomState(42)
t = 300 * rand.rand(300)
y = 0.005*np.sin(2 * np.pi * t/2.) + 0.002 * rand.randn(len(t))
dy = 0.001 + 0.002* rand.rand(len(t))
i = range(300)

data = Table([i, t, y, dy], names=['i', 'time', 'mag', 'error'])
ascii.write(data, 'example/random2.dat')


rand = np.random.RandomState(42)
t = 300 * rand.rand(300)
y = 0.002*np.sin(2 * np.pi * t/2.) + 0.002 * rand.randn(len(t))
dy = 0.001 + 0.002* rand.rand(len(t))
i = range(300)

data = Table([i, t, y, dy], names=['i', 'time', 'mag', 'error'])
ascii.write(data, 'example/random3.dat')


rand = np.random.RandomState(42)
t = 1000 * rand.rand(300)
y = 0.005*np.sin(2 * np.pi * t/120.) + 0.002 * rand.randn(len(t))
dy = 0.001 + 0.002* rand.rand(len(t))
i = range(300)

data = Table([i, t, y, dy], names=['i', 'time', 'mag', 'error'])
ascii.write(data, 'example/random4.dat')
