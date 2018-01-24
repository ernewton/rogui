from rotationgui import *

######
# fit data
######
import scipy.signal as signal
from astropy.stats import LombScargle
def fit_period(lc_data,
               pmin = 0.1, pmax=1000.,
               vbest = None):

    lc = lc_data ## place holder for more complicated stuff

    # get the best fit
    scaled_mags = (lc['flux']-lc['flux'].mean())/lc['flux'].std()
    freqs, periodogram = LombScargle(np.array(lc['time']).astype('float64'), np.array(scaled_mags).astype('float64')).autopower(nyquist_factor=2)

    # test frequencies
    #freqs = 2.*math.pi/np.linspace(pmin, pmax, 1000)
    #periodogram = signal.lombscargle(np.array(lc['time']).astype('float64'), np.array(scaled_mags).astype('float64'), freqs)

    phase = 0.
    amplitude = 0.1
    frequency = freqs[np.argmax(periodogram)]
    
    if vbest is not None:
        frequency = vbest
    
    print "Best fit period:", 1./frequency

    return frequency, phase, amplitude


######
# read in data
######
def read_text(myfile):
    try:
        lc = np.genfromtxt(myfile,
                           usecols = (1,2,3),
                           skip_header=2,
                           dtype={"names": ("time", "flux", "e_flux"),
                                  "formats": ("f8", "f4", "f4")})
        
        return lc
    except:
        print myfile
        return False

######
# plots
######
import math
def rotation_plot(lc_data, 
                  fig, 
                  plot_binned=False,
                  plot_model=False,
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
        plt.xlabel('Data number')
        plt.ylabel('Magnitude')
        
        # raw light curve: flux v. time
        raw = fig.add_subplot(nrows,ncols,1+ncols+i, sharey=dat)
        plt.scatter(lc['time'], lc['flux'], color=c)
        plt.xlabel('Time')
        plt.ylabel('Magnitude')
        if plot_model:
            axrange=np.linspace(np.min(lc['time']),np.max(lc['time']),1000)
            y = amplitude*np.sin(2*math.pi*(axrange)*frequency + phase)
            plt.plot(axrange,y,c='k')
    
        # phased light curve: flux v. phase
        phased = fig.add_subplot(nrows,ncols,1+2*ncols+i, sharey=dat)
        time_folded = np.fmod((lc['time'])*frequency, 1.0)
        plt.scatter(time_folded, lc['flux'], color=c)
        plt.xlabel('Phase')
        plt.ylabel('Magnitude')
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
    
    return my_subplots


# files to include are the arguments
try:
    filelist = []
    for arg in sys.argv[1:]:
        print "Reading file ", arg
        f = open(arg,'r')
        for line in f:
            # remove newlines, allow comma separated  
            xx = line.rstrip('\n').split(',')   
            for x in xx:
                filelist.append(x)
except:
    raise("No files provided")

    
# run the GUI
root = Tk() # create a root window
pg = RGui(root, rotation_plot, read_text, fit_period, filelist)
pg.start()
