

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (binary_erosion, generate_binary_structure, iterate_structure)

import hashlib
from operator import itemgetter
from _ast import operator




MIN_AMP = 10
SORT_PEAKS = True
DEFAULT_FS = 44100

# Size of the FFT window
DEFAULT_WINDOW = 4096

# Ration by which the sequential window overlaps the last and next window.
# Higher raitos are least preferred because there is tendancy for an increase in more
# fingerprint matches 
DEFAULT_OVERLAP_RATIO = 0.5

# As the fan value increases, more fingerprints will added to the database to be 
# compared among each other, which bolsters accuracy 

DEFAULT_FAN_VALUE = 15



# Number of cells around an amplitude peak in the spectrogram i
# order for it be considered a spectral peak

PEAK_CELLS_SIZE = 20
MIN_TIME_DELTA = 0
MAX_TIME_DELTA = 200


def fingerprint(channels, fs = DEFAULT_FS, 
                window_size = DEFAULT_WINDOW, 
                ratio = DEFAULT_OVERLAP_RATIO,
                val = DEFAULT_FAN_VALUE,
                min_amp = MIN_AMP):
    # FFT the signal, find amplitudes in spectrograms ( or local maxima), and then
    # return hashes
    
    
    arr = mlab.specgram(channels, NFFT = window_size, Fs = fs, window = mlab.window_hanning,
                        noverlap = int(window_size * ratio))[0]

    # log transform output because specgram returns linear array
    arr = 10 * np.log10(arr)
    arr[arr == -np.inf] = 0 # replace infs with zeros
    
    # find local maxima 
    local_maxima = get_amplitudes(arr, plot = False, amp_minimum = min_amp)
    
    
    # return hashes
    return get_hashes(local_maxima, val)


def get_amplitudes(array, plot = False, amp_minimum = MIN_AMP):
    structure =  generate_binary_structure(2,1)
    surroundings = iterate_structure(structure, PEAK_CELLS_SIZE)
    
    local_max = maximum_filter(array, footprint = surroundings) == array
    
    background = (array == 0)
    eroded_b = binary_erosion(background, structure = surroundings, border_value = 1)
    
    
    # Getting the peaks or points in the spectrogram with the highest amplitudes
    found_peaks = local_max ^ eroded_b
    
    highest_amps = array[found_peaks]
    j, i = np.where(found_peaks)
    
    
    # filtering highest points in specgram
    highest_amps =  highest_amps.flatten()
    points = zip(i,j, highest_amps)
    new_points = [x for x in points if x[2] > amp_minimum]
    
    # find frequency and time 
    freq_loc = [x[0] for x in new_points]
    time_loc = [x[1] for x in new_points]
     
    # In array of new peaks in specgram, frequency, time, and amplitude are stored in the 
    # first three indices 
    
    
    # Handle plotting case 
    return list(zip(freq_loc, time_loc))




def get_hashes(high_pts, val = DEFAULT_FAN_VALUE):
    """  Hash list structure:
            [(hash, anchor time)] of peaks with highest amplitudes
            
    """
    if SORT_PEAKS:
        sorted(high_pts, key = itemgetter(1))
    
    for i in range(len(list(high_pts))):
        for j in (1, val):
            if (i + j) < len(list(high_pts)):
                
                frequency1 = high_pts[i][0]
                frequency2 = high_pts[i + j][0]
                t1 = high_pts[i][1]
                t2 = high_pts[i + j][1]
                time_delta = t2 - t1
                
            
                # checking if t1 and t2 within bounds
                #f1 = frequency1.tostring().decode("unicode_escape")
                #f2 = frequency2.tostring().decode("unicode_escape")
                #t_delta = time_delta.tostring().decode("unicode_escape")
                
                if t1 >= MIN_TIME_DELTA and t2 <= MAX_TIME_DELTA:
                    hash = hashlib.sha1()
                    hash.update("%s|%s|%s" % (str(frequency1), str(frequency2), str(time_delta))).encode('utf-8')
                    yield (hash.hexdigest()[0:20], t1)
       
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    