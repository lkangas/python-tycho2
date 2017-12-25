# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 18:07:42 2017
    
@author: vostok
"""
from numpy import empty_like

def icp_metric(image_stars, catalog_stars, vectors=False):
    closest_distances = empty_like(image_stars['X'])
    closest_indices = empty_like(image_stars['X'])
    
    catalog_X, catalog_Y = catalog_stars
    for i, star in enumerate(image_stars):
        dx = star['X'] - catalog_X
        dy = star['Y'] - catalog_Y
        r2 = dx**2 + dy**2
        
        closest_distances[i] = r2.min()
        closest_indices[i] = r2.argmin()
    
    if not vectors:
        return closest_distances.sum()
    
    return closest_distances.sum(), \
        closest_distances, closest_indices.astype('int')
