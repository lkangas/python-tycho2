# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 15:19:55 2017

@author: vostok
"""

import os
import tempfile
from astropy.io import fits

def extract_stars(input_array):
    (infilehandle, infilepath) = tempfile.mkstemp(suffix='.fits')
    os.close(infilehandle)

    fits.writeto(infilepath, \
                 input_array.astype('float32'), \
                 fits.Header(), \
                 overwrite=True)

    return_code = os.system('image2xy -O {}'.format(infilepath))
    if return_code != 0:
        raise "image2xy returned with error code %d" % return_code

    result = fits.open(infilepath.replace('.fits', '.xy.fits'))[1].data

    os.unlink(infilepath)
    
    result['X'] -= 1
    result['Y'] -= 1
    
    return result