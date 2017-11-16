import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import lya_mock_functions as mock

#Open data file
hdulist = fits.open('/Users/jfarr/Projects/repixelise/test_input/out_srcs_s0_15.fits')

#Extract redshift from data file
z = hdulist[4].data['Z']
z = np.asarray(z)

#Get number of quasars, and redshift array
z_qso = hdulist[1].data['Z_COSMO']
N_qso = len(z_qso)
print('There are %d quasars in the sample.' % N_qso)

#Get the length of each skewer.
N_pix_skewer = hdulist[2].data.shape[1]
print('There are %d pixels in each skewer.' % N_pix_skewer)

#Show the structure of the data
print(hdulist[2].header.keys)

#Get delta (the deviation from average density field) for the highest redshift quasar in the sample.
id = np.argmax(hdulist[1].data['Z_COSMO'])
delta = hdulist[2].data[id]

#Show delta vs r
print('mean delta =', np.mean(delta))
print('var delta =', np.var(delta))
plt.figure()
plt.plot(hdulist[4].data['R'],hdulist[2].data[id])
plt.xlabel('$r\\,\\,[{\\rm Mpc}/h]$')
plt.ylabel('$\\delta$')

#CHECK DELTA VS DENSITY
#Show delta vs z
plt.figure()
plt.plot(z,delta)
plt.xlabel('z')
plt.ylabel('$\\delta$')
print(" ")

#Show density vs z
density = (delta + 1)
print('mean density =', np.mean(density))
print('var density =', np.var(density))
plt.figure()
plt.semilogy(z,density)
plt.xlabel('z')
plt.ylabel('density')
print(" ")

#Convert from a lognormal density field to optical depth
tau = mock.get_tau(z,density)
print('mean tau =', np.mean(tau))
print('var tau =', np.var(tau))
plt.figure()
plt.semilogy(z,tau)
plt.xlabel('z')
plt.ylabel('optical depth')
print(" ")

#Convert from optical depth to transmitted flux fraction
flux = np.exp(-tau)
print('mean flux =', np.mean(flux))
print('var flux =', np.var(flux))
plt.figure()
plt.plot(z,flux)
plt.xlabel('z')
plt.ylabel('transmitted flux fraction')
print(" ")

#Show a test skewer spectrum
freq = 1215.67*(1+z)
plt.figure()
plt.plot(freq,flux)
plt.xlabel('frequency')
plt.ylabel('transmitted flux fraction')
print(" ")

#Calculate density statistics
binned_z, binned_mean_density, binned_density_var, binned_delta_var = mock.density_stats(z,z_qso,(hdulist[2].data)+1)

#Show the calculated statistics against z
plt.figure()
plot_binned_mean_density = plt.plot(binned_z, binned_mean_density)
plt.xlabel('z')
plt.ylabel('Mean density')
plt.figure()
plot_binned_density_var = plt.plot(binned_z, binned_density_var)
plt.xlabel('z')
plt.ylabel('Density variance')
plt.figure()
plot_binned_delta_var = plt.plot(binned_z, binned_delta_var)
plt.xlabel('z')
plt.ylabel('Delta variance')
print(" ")


#Show a sequence of histograms of delta
#Define redshift bin boundaries: zhb(0)<=z<zhb(1), zhb(1)<=z<zhb(2) etc.
z_hist_bins_boundaries = [0,2,3]
N_bins = len(z_hist_bins_boundaries)

#For each quasar, set up a mask to remove entries of 0 delta beyond the quasar.
mask = np.ones(hdulist[2].data.shape)
max_pixel_qso = [0.]*N_qso
lower_bound = [0]*N_bins
upper_bound = [0]*N_bins

for j in range(N_qso):
    max_pixel_qso[j] = (np.argmax(z>z_qso[j]))%N_pix_skewer
    mask[j,max_pixel_qso[j]+1:]=np.zeros(1,(mask.shape[1]-max_pixel_qso[j]-1))

for i in range(N_bins):
    #get boundaries in skewer length terms
    lower_bound[i] = max(np.argmax(z>z_hist_bins_boundaries[i])-1,0)
    if i+1 < N_bins:
        upper_bound[i] = np.argmax(z>z_hist_bins_boundaries[i+1])-1
    else:
        upper_bound[i] = len(z)-1

    #print histogram
    plt.figure()
    plt.hist(np.ravel(hdulist[2].data[:,lower_bound[i]:upper_bound[i]]),bins=1000,weights=np.ravel(mask[:,lower_bound[i]:upper_bound[i]]))
    plt.yscale('log',nonposy='clip')
    plt.xlabel('$\\delta$')
    #y-axis is labelled differently depending on which bin we're looking at.
    if i+1 < N_bins:
        plt.ylabel('frequency for %d<z<%d' % (z_hist_bins_boundaries[i], z_hist_bins_boundaries[i+1]))
    else:
        plt.ylabel('frequency for z>%d' % z_hist_bins_boundaries[i])

#Make one plot with all of the
#plt.figure()
#plt.yscale('log',nonposy='clip')
#plt.xscale('log',nonposy='clip')
#for i in range(N_bins):
#    plt.hist(np.ravel(hdulist[2].data[:,lower_bound[i]:upper_bound[i]]),bins=100,weights=np.ravel(mask[:,lower_bound[i]:upper_bound[i]]),normed=True,histtype='step')
#plt.xlabel('$\\delta$')
#plt.ylabel('frequency')
#plt.xlim(-1,50)

plt.show()


#Old stuff below

#First HDU contains the source catalog
#print(hdulist[1].header.keys)
#plt.figure(); plt.hist(hdulist[1].data['Z_COSMO'],bins=100)
#print(" ")

#Second HDU contains the density skewers as a FITS image
#The skewers have the same ordering as the sources in the catalog
#(i.e. skewer hdulist[2].data[i,:] corresponds to source hdulist[1].data[i])

#Third HDU contains the velocity skewers. The units of the velocity are
#such that the skewers contain the redshift distortion associated with
#the peculiar velocity field
#print(hdulist[3].header.keys)
#plt.figure(); plt.plot(hdulist[4].data['R'],hdulist[3].data[id]);
#plt.xlabel('$r\\,\\,[{\\rm Mpc}/h]$',fontsize=18);
#plt.ylabel('$\\delta z_{\\rm RSD}$',fontsize=18)
#print(" ")

#Fourth HDU is a table containing background cosmological quantities at
#the distances where the skewers are sampled (see the use of
#hdulist[4].data['R'] in the previous examples
#print(hdulist[4].header.keys)
#plt.figure();
#plt.plot(hdulist[4].data['Z'],hdulist[4].data['R']*0.001,label='$r(z)\\,[{\\rm Gpc}/h]$')
#plt.plot(hdulist[4].data['Z'],hdulist[4].data['D'],label='$D_\\delta(z)$')
#plt.plot(hdulist[4].data['Z'],hdulist[4].data['V'],label='$D_v(z)$')
#plt.legend(loc='lower right')
#plt.xlabel('$z$',fontsize=18)
#print(" ")

#
