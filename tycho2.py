# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 12:42:31 2017

@author: lauri.kangas
"""

import numpy as np
import coordinate_transformations as coord

class tycho2:
    def __init__(self, index_filename, catalog_filename, supplement_filename):
        self._index = np.load(index_filename)
        self._catalog = np.load(catalog_filename, mmap_mode='r')
        self._supplement = np.load(supplement_filename)
        
    def regions_within_radius(self, center, radius):
        radius = np.radians(radius)
        center_RA, center_DEC = center
        
        region_RAs = self._index[:,2] # GSC region central coords
        region_DECs = self._index[:,3]
        region_radii = self._index[:,4] # GSC region corner radius
        
        # lets rotate coordinates so that center_RA and center_DEC are at origin
        region_xyz = coord.rotate_RADEC(region_RAs, region_DECs, center_RA, center_DEC)
        R = coord.xyz_radius_from_origin(*region_xyz)
        
        regions, = np.nonzero(R < radius + region_radii)
        
        # GSC index has an extra row in the end (index 9537) marked at RADEC 0,0. filter it out.
        regions = regions[regions < self._index.shape[0]-1]
        
        return regions
    
    def stars_in_regions(self, regions, LM=None):
        tyc_start_inds = self._index[:,0] # starting indices for tycho2 stars in GSC region
        sup_start_inds = self._index[:,1] #  ... for tycho2 supplement stars
        
        tycho_ranges = [np.arange(tyc_start_inds[i], tyc_start_inds[i+1]) for i in regions]
        supplement_ranges = [np.arange(sup_start_inds[i], sup_start_inds[i+1]) for i in regions]
        
        tycho_indices = np.concatenate(tycho_ranges).astype('int')
        suppl_indices = np.concatenate(supplement_ranges).astype('int')
        
        # append supplement to catalog, making an Nx3 array (ra, dec, mag)
        supplemented_catalog = np.vstack([self._catalog[tycho_indices], \
                                          self._supplement[suppl_indices]])
    
        if LM:
            # strip out stars below LM
            mags = supplemented_catalog[:,2]
            trimmed_catalog = supplemented_catalog[mags < LM]
        else:
            trimmed_catalog = supplemented_catalog
            
        RAs = trimmed_catalog[:,0]
        DECs = trimmed_catalog[:,1]
        mags = trimmed_catalog[:,2]
        
        return RAs, DECs, mags
    
#        xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
#        image_x, image_y = coord.xyz_to_imagexy(*xyz, \
#                                                rotation=rotation, \
#                                                projection=self._projection)
        
        
            
        
        
        
        
        
        
        
        
        
        
        
        