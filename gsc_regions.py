# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 22:49:15 2017

@author: lauri.kangas
"""

import numpy as np

from projections import stereographic, unity
import coordinate_transformations as coord


def find_GSC_regions(index, center, rotation, fov, \
                     area='rectangle', projection=stereographic):
    # return indices of GSC regions that are inside fov
    # angular fov is given in radians
    # 'rectangle' selects tight subset of indices (projection matters),
    # 'circle' selects all indices within a diagonal radius (projection doesn't matter)
    
    
    center_RA, center_DEC = center
    
    region_RAs = index[:,2] # GSC region central coords
    region_DECs = index[:,3]
    region_radii = index[:,4] # GSC region corner radius
    
    # lets rotate coordinates so that center_RA and center_DEC are at origin
    region_xyz = coord.rotate_RADEC(region_RAs, region_DECs, center_RA, center_DEC)
    
    # project region xyz coordinates to image plane
    region_image_x, \
    region_image_y, \
    R = coord.xyz_to_imagexy(*region_xyz, \
                                    rotation=rotation, \
                                    projection=projection, \
                                    include_R=True)
    
    fov = np.array(fov) # just in case
    half_fov_angle = fov/2

    half_fov_imageplane = projection(half_fov_angle)

    if area == 'rectangle':
        fov_h, fov_v = half_fov_imageplane
        indices = np.logical_and( \
                        np.abs(region_image_x) < fov_h + region_radii, \
                        np.abs(region_image_y) < fov_v + region_radii)
    else: # circle
        half_diagonal_imageplane = np.hypot(*half_fov_imageplane)
        half_diagonal_angle = projection(half_diagonal_imageplane, inverse=True)
        indices = R < half_diagonal_angle + region_radii
    
    return np.nonzero(indices) # return numbers instead of boolean tables

def regions_within_radius(index, center, radius):
        center_RA, center_DEC = center
    
    region_RAs = index[:,2] # GSC region central coords
    region_DECs = index[:,3]
    region_radii = index[:,4] # GSC region corner radius
    
    # lets rotate coordinates so that center_RA and center_DEC are at origin
    region_xyz = coord.rotate_RADEC(region_RAs, region_DECs, center_RA, center_DEC)
    R = coord.xyz_radius_from_origin(*region_xyz)
    
    return np.nonzero(R < radius + region_radii)

