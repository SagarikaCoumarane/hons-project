
import numpy as np


# This function simulates the spiking activity of a set of place cells on a linear track under the independent coding model.                                                   
# Inputs:
# v0 = running speed at t=0
# a = acceleration (a constant, usually zero)
# dth = time bin size in degrees of LFP theta
# phase locking = phase locking of cells
# Ncyc = length of simulation in number of LFP theta cycles
# theta_0 = LFP theta phase at t=0
# Nspikes = number of spikes fired on average pass through a place field (independent of running speed)
# xc = vector of place field centres (one for each cell)

# Outputs:
# spikes = binary matrix of spiking activity over time and cell number
# r = matrix of continuous intensity signals over time and cell number
def generate_independent_spikes(v0, a, dth, phase_locking, Ncyc, theta_0, Nspikes, xc):
    #LFP Theta freq (Hz)
    f_theta = 8
    
    #vector of simulation time bins
    start = (-Ncyc*0.5)/f_theta+dth/(f_theta*360)
    end = dth/(f_theta*360)
    step = (Ncyc*0.5)/f_theta
    t = np.arange(start,end,step)

    v = v0 + a@t  # running speed at time t
    xrat = v*t + 0.5*a@t**2;   # rat location at time t

    #-----------Set Parameters----------------
    sigma0 = 9   # Gaussian place field width (cm)
    sigma = sigma0*np.ones(xc.shape);  # Gaussian place field width of each cell (replace ones vector by some other vector to model a heterogeneous population)

    dphi = 2*np.pi # total phase precessed over place field (radians)

    R0 = 18.75    # radius of phase precession in cm (from Maurer et al., 2006)
    R = R0@(sigma/sigma0) # radius of phase precession for individual cells (used in heterogeneous case)

    k = dphi/(2*R)    # wavenumber (vector with entries for each cell, to allow for heterogeneous case)
    
    #-----------Initialise data matrices---------------

    r = np.zeros(max(xc.shape), max(t.shape))         # firing rate matrix (cell by time sample)
    psi = r                                  # spatiotemporal theta phase matrix (cell by time sample)
    Phase_Field = r                          # phasic tuning curve matrix (cell by time sample)
    Place_Field = r                          # spatial tuning curve matrix (cell by time sample)
    A = r  #firing rate amplitude (changes with running speed)   

    #-----------Calculate travelling wave across all place cells and times and get firing rate matrix----------
    for j in range(max(t.shape)):            
            
        psi[...,j] = k.flatten(1)*(xc.flatten(1) - xrat[j]) - 2*np.pi*f_theta*t[j] - theta_0  # linear phase model
            
        Phase_Field[...,j] = np.exp(phase_locking.flatten(1)*np.cos(psi[...,j]))  # von phasic Mises tuning curve model (circular Gaussian)
        Place_Field[...,j] = np.exp(-(xc.flatten(1) - xrat(j))**2./(2*sigma.flatten(1)**2))  # Gaussian spatial tuning curve model
        
        A[...,j] = Nspikes*abs(v(j))/(np.sqrt(2*np.pi*sigma**2) * np.i0(0, phase_locking.flatten(1)))  # velocity modulation - based on integral approximation to generate fixed spike counts Nspikes across different running speeds
        
        r[...,j] = A[...,j]*Phase_Field[...,j]*Place_Field[...,j]   # firing rate of each cell at each time       
         

    #----------Poisson Spike Generation------------

    rv = np.random(r.shape)  # matrix of random variables

    spikes = (r*dth/(f_theta*360) > rv) # spiking activity under a space-time poisson process

    return spikes, r

print(generate_independent_spikes())