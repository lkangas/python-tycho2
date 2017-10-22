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
    
index = np.load('tyc2index.npy')
catalog = np.load('tyc2.npy', mmap_mode='r')
suppl = np.load('tyc2sup.npy')

center_RADEC = np.radians([90, 0])
rotation = np.radians(0)

fov_degrees = np.array([70, 70])
fov_radians = np.radians(fov_degrees)
half_fov_radians = fov_radians/2

projection = stereographic
projection = unity

image_plane_half_fov = projection(half_fov_radians)

LM = 12
factor = 4

TYC2 = tycho2('tyc2index.npy', 'tyc2.npy', 'tyc2sup.npy', projection=projection)
image_x, image_y, mags = TYC2.stars_in_fov(center_RADEC, fov_radians, rotation, LM=LM)

plt.clf()
plt.scatter(image_x, image_y, (LM-mags)**2.5/LM*factor, alpha=1)

plt.axis('equal')

import matplotlib.patches as patches

plt.gca().add_patch(patches.Rectangle(-image_plane_half_fov, *(2*image_plane_half_fov), fill=False))
plt.tight_layout()
plt.axis('off')