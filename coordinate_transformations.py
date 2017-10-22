# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 22:35:50 2017

@author: lauri.kangas
"""

from numpy import sin,cos,arccos,arctan2,mod,pi
from projections import stereographic

def rotate_RADEC(RAs, DECs, center_RA, center_DEC, output='xyz'):
    # rotate RA,DEC coordinates to turn center_RA,center_DEC to origin
    
    # RA can be rotated first
    RArotated_RAs = mod(RAs - center_RA, 2*pi)
    
    # convert to rectangular coordinates
    RArotated_x, \
    RArotated_y, \
    RArotated_z = RADEC_to_xyz(RArotated_RAs, DECs)
        
    # now we can rotate by center_DEC.
    RADECrotated_x, \
    RADECrotated_y, \
    RADECrotated_z = tilt_xyz_y(RArotated_x, \
                                RArotated_y, \
                                RArotated_z, center_DEC)
    
    if output.lower() == 'xyz':
        return RADECrotated_x, RADECrotated_y, RADECrotated_z
    elif output.lower() == 'radec':
        # calculate RA/DEC again
        return None
    
def RADEC_to_xyz(RA, DEC):
    x = cos(RA)*cos(DEC)
    y = sin(RA)*cos(DEC)
    z = sin(DEC)
    
    return x,y,z


def tilt_xyz_y(x, y, z, angle, x_only=False):
    # tilt xyz coordinates along y_axis by amount angle
    # x_only: if only radius matters, (for gsc region selection),
    #         don't calculate y and z
    
    xx = x*cos(angle)+z*sin(angle)
    if x_only:
        return xx
    
    yy = y                        
    zz = -x*sin(angle)+z*cos(angle) 
    
    return xx,yy,zz

def xyz_to_imagexy(x, y, z, \
                   rotation=0, projection=stereographic, include_R=False):
    # project xyz coordinates on a sphere to image plane
    # R can be returned for filtering GSR regions

    # calculate angular distance from image center along sphere
    R = arccos(x)
    
    r = projection(R)
    
    # polar angle of region coordinates in image plane
    T = arctan2(z, y)
    
    T += rotation
    
    image_x = -r * cos(T)
    image_y = r * sin(T)
    
    if include_R:
        return image_x, image_y, R
    
    return image_x, image_y
