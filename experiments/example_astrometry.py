# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 00:17:33 2017

@author: lauri.kangas
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from tycho2 import tycho2
from projections import stereographic, unity, rectilinear
import coordinate_transformations as coord
import astrometry

API_KEY = 'ailckcattnyvxxfu'
filename = 'orion2.jpg'

#solution, session = astrometry.solve(filename, api_key=API_KEY)
print(solution)
projection = rectilinear

orion = mpimg.imread(filename)
resolution = np.array(orion.shape[1::-1])
aspect_ratio = resolution[1]/resolution[0]

#sensor_size = resolution/resolution.max()*.342

center_RADEC = np.radians([solution['ra'], solution['dec']])
rotation = np.radians(-solution['orientation'])
radius = solution['radius']

fov_degrees, sensor_size = coord.radius2fov(radius, aspect_ratio, projection=projection)



#sensor_size *= 1.4

T = tycho2('tyc2index.npy', 'tyc2.npy', 'tyc2sup.npy')


fov_radians = np.radians(fov_degrees)

#radius = coord.fov_radius(fov_degrees)

LM = 6
factor = 20

regions = T.regions_within_radius(center_RADEC, radius)
RAs, DECs, mags = T.stars_in_regions(regions, LM=LM)

xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
image_xy = coord.xyz_to_imagexy(*xyz, rotation=rotation)

X, Y = coord.imagexy_to_pixelXY(image_xy, resolution, pixel_scale=solution['pixscale'])

X_within = np.logical_and(X >= 0, X < resolution[0])
Y_within = np.logical_and(Y >= 0, Y < resolution[1])
XY_within = np.logical_and(X_within, Y_within)

X = X[XY_within]
Y = Y[XY_within]
mags = mags[XY_within]

plt.clf()

plt.imshow(orion)

sizes = (LM-mags)**2.5/LM

plt.scatter(X, Y, 50, facecolors='none', edgecolors='red')
#
#plt.axis('equal')
#
#import matplotlib.patches as patches
#
#image_plane_half_fov = projection(np.radians(fov_degrees/2))
#plt.gca().add_patch(patches.Rectangle(-image_plane_half_fov, *(2*image_plane_half_fov), fill=False))
#plt.tight_layout()
#plt.axis('tight')
##plt.axis('off')