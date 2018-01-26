from astropy.io import fits

from rotationgui import *
from plotgui import PlotGui

#import scipy.signal as signal
from astropy.stats import LombScargle

######
# fit data
######
def fit_period(lc_data,
               pmin = 0.1, pmax=1000.,
               vbest = None,
               return_pgram = False):

    lc = lc_data ## place holder for more complicated stuff
    fin =np.isfinite(lc['flux'])
    # get the best fit
    scaled_mags = (lc['flux']-lc['flux'][fin].mean())/lc['flux'][fin].std()
    freqs, periodogram = LombScargle(np.array(lc['time'][fin]).astype('float64'), np.array(scaled_mags[fin]).astype('float64')).autopower(minimum_frequency=1./pmax,maximum_frequency=1./pmin)

    # test frequencies
    #freqs = 2.*math.pi/np.linspace(pmin, pmax, 1000)
    #periodogram = signal.lombscargle(np.array(lc['time']).astype('float64'), np.array(scaled_mags).astype('float64'), freqs)

    phase = 0.

    low, high = np.percentile(lc['flux'][fin], [0.05,0.95])
    amplitude = (high - low) /2.
    frequency = freqs[np.argmax(periodogram)]
    
    if vbest is not None:
        frequency = vbest

    print freqs, periodogram
    print "Best fit period:", 1./frequency, "days"

    if return_pgram:
        return freqs, periodogram
    return frequency, phase, amplitude


######
# read in data
######
def read_text(myfile):
    print "Reading: ", myfile
    if True:

        # read in the time and flux and error
        hdul = fits.open(myfile)
        data = hdul[1].data
        if 'polar' in myfile:
             lc = {'time':data['FILTIME'], 'flux':data['FILFLUX'], 'e_flux':data['FILFLUXERROR']}           
        elif 'varcat' in myfile:
            lc = {'time':data['TIME'], 'flux':data['DETFLUX'], 'e_flux':data['DETFLUX_ERR']}
        elif 'everest' in myfile: # Luger
            lc = {'time':data['TIME'], 'flux':data['FCOR'], 'e_flux':data['FRAW_ERR']}            
        elif 'hlsp_k2sff' in myfile: # Vanderberg & Johnson 
            lc = {'time':data['T'], 'flux':data['FCOR'], 'e_flux':np.ones_like(len(data['T']))}
        else: # assume Kepler pipeline
            lc = {'time':data['TIME'], 'flux':data['PDCSAP_FLUX'], 'e_flux':data['PDCSAP_FLUX_ERR'],
                      'mom_time':data['TIME'], 'mom1':data['MOM_CENTR1'], 'mom2':data['MOM_CENTR2']}
        hdul.close()
        lc['file'] = myfile
        print "name", lc['file']

        # get the moments from the Kepler data reduction
        if 'mom1' not in lc.keys():
            basedd = "/".join(myfile.split('/')[0:-2])
            dd = myfile.split('/')[-2] # directory
            ff = dd.split('polar')[-1].split('everest')[-1].split('k2sff')[-1].split('varcat')[-1]
            fff = ff.split('_')[0]
            ktwoff = "/".join([basedd, 'ktwo'+ff, 'ktwo'+fff+'_llc.fits'])

            hdul = fits.open(ktwoff)
            data = hdul[1].data
            lc['mom1'] = data['MOM_CENTR1']
            lc['mom2'] = data['MOM_CENTR2']
            lc['mom_time'] = data['TIME']
            hdul.close()


        mag = -2.5*np.log10(lc['flux']/np.nanmedian(lc['flux']))
        lc['flux'] = mag
        lc['e_flux'] = np.ones_like(mag)
        # need to convert error too
        
        if False:
            std = 1.48*np.nanmedian( np.abs(mag - np.nanmedian(mag)) )
            lc['flux'][np.abs(lc['flux']) < -5*std] = np.nan
            print "Removing outliers < 5 x", std

        return lc
    
    else:
        print "Failed to read: ", myfile
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
            
        c = range(0,len(lc['time']))
        cm = 'viridis'
        # raw light curve: flux v. data number
        dat = fig.add_subplot(nrows,ncols,1+i)
        plt.title(lc['file'])
        #plt.scatter(np.arange(len(lc['flux'])), lc['flux'], c=c, cmap=cm, vmax=1.3*len(lc['flux']))
        #plt.xlabel('Data number')
        #plt.ylabel('Magnitude')

        fin =np.isfinite(lc['flux'])
        scaled_mags = (lc['flux']-lc['flux'][fin].mean())/lc['flux'][fin].std()
        freqs, periodogram = LombScargle(np.array(lc['time'][fin]).astype('float64'), np.array(scaled_mags[fin]).astype('float64')).autopower(minimum_frequency=1./90.,maximum_frequency=1./0.01)
        plt.plot(1./freqs, periodogram, label='Stellar signal')
        fin =np.isfinite(lc['mom1'])
        freqs, periodogram = LombScargle(np.array(lc['mom_time'][fin]).astype('float64'), np.array(lc['mom1'][fin]).astype('float64')).autopower(minimum_frequency=1./90.,maximum_frequency=1./0.01)
        plt.plot(1./freqs, periodogram, ':', c='indianred', label='Spacecraft motion')
        plt.xlabel('Period')
        plt.ylabel('Power')
        #plt.plot([1./(24.5+frequency), 1./(24.5+frequency)], [0,1], '--', c='r')
        #plt.plot([1./(24.5-frequency), 1./(24.5-frequency)], [0,1], '--', c='r')
        #plt.plot([1./(2*frequency), 1./(2*frequency)], [0,1], ':', c='r')
        #plt.plot([1./(3*frequency), 1./(3*frequency)], [0,1], ':', c='r')
        #plt.plot([1./(4*frequency), 1./(4*frequency)], [0,1], ':', c='r')
        plt.xscale('log')

        
        # raw light curve: flux v. time
        raw = fig.add_subplot(nrows,ncols,1+ncols+i)
        plt.scatter(lc['time'], lc['flux'], c=c, cmap=cm, vmax=1.3*len(lc['flux']))
        plt.xlabel('Time')
        plt.ylabel('Magnitude')
        if plot_model:
            axrange=np.arange(np.min(lc['time']),np.max(lc['time']),0.1/frequency)
            y = amplitude*np.sin(2*math.pi*(axrange)*frequency + phase)
            plt.plot(axrange,y,c='k')
    
        # phased light curve: flux v. phase
        phased = fig.add_subplot(nrows,ncols,1+2*ncols+i, sharey=raw)
        time_folded = np.fmod((lc['time'])*frequency, 1.0)
        plt.scatter(time_folded, lc['flux'], c=c, cmap=cm, vmax=1.3*len(lc['flux']))
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
