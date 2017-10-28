# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 00:17:33 2017

@author: lauri.kangas
"""

import matplotlib.pyplot as plt
import numpy as np

from tycho2 import tycho2
from projections import stereographic, unity
import coordinate_transformations as coord
    
T = tycho2('tyc2index.npy', 'tyc2.npy', 'tyc2sup.npy')
center_RADEC = np.radians([90, 0])
rotation = np.radians(0)

fov_degrees = np.array([23, 5])
fov_radians = np.radians(fov_degrees)

radius = coord.fov_radius(fov_degrees)

projection = stereographic
projection = unity

LM = 9
factor = 4

regions = T.regions_within_radius(center_RADEC, radius)
RAs, DECs, mags = T.stars_in_regions(regions, LM=LM)

xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
image_x, image_y = coord.xyz_to_imagexy(*xyz, rotation=rotation)

plt.clf()
plt.scatter(image_x, image_y, (LM-mags)**2.5/LM*factor)

plt.axis('equal')

import matplotlib.patches as patches

image_plane_half_fov = projection(np.radians(fov_degrees/2))
plt.gca().add_patch(patches.Rectangle(-image_plane_half_fov, *(2*image_plane_half_fov), fill=False))
plt.tight_layout()
#plt.axis('off')