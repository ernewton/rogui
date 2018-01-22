import numpy as np
rand = np.random.RandomState(42)
t = 1000 * rand.rand(300)
y = 0.005*np.sin(2 * np.pi * t/50.) + 0.001 * rand.randn(300)
dy = np.random.normal(0.001)

for i, ti, yi, dyi in enumerate(*zip(t,y,dy)):
    
