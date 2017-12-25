# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 15:33:29 2017

@author: vostok
"""

import os
from astropy.io import fits
import tempfile
from PIL import Image
import numpy as np

def image2xy(data):
    (infilehandle, infilepath) = tempfile.mkstemp(suffix='.fits')
    os.close(infilehandle)

    fits.writeto(infilepath, data.astype('float32'), fits.Header(), overwrite=True)

    return_code = os.system('image2xy -O {}'.format(infilepath))
    if return_code != 0:
        raise "image2xy returned with error code %d" % return_code

    result = fits.open(infilepath.replace('.fits', '.xy.fits'))[1].data

    os.unlink(infilepath)

    return result

#print image2xy(pyfits.open(sys.argv[1])[0].data)
filename = 'satellite-astrophoto4.jpg'
img = Image.open(filename)
img.load()
data = np.asarray(img).mean(2)
stars = np.array(image2xy(data))
    