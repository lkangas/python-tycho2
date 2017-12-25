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
from image_analysis import extract_stars

def closest_distance(image_star, catalog_stars_x, catalog_stars_y, arg=False):
    distances = np.hypot(image_star['X'] - catalog_stars_x, image_star['Y'] - catalog_stars_y)
    
    if arg:
        return distances.min(), distances.argmin()
    else:
        return distances.min()

API_KEY = 'ailckcattnyvxxfu'
filename = 'otava2.jpg'

#solution, session = astrometry.solve(filename, api_key=API_KEY)
print(solution)
projection = rectilinear

image_data = mpimg.imread(filename)
grayscale_data = image_data.mean(axis=2)
resolution = np.array(image_data.shape[1::-1])
aspect_ratio = resolution[1]/resolution[0]

center_RADEC = np.radians([solution['ra'], solution['dec']])
angle = np.radians(-solution['orientation'])

zoom = solution['pixscale']

radius = solution['radius']

fov_degrees, sensor_size = coord.radius2fov(radius, aspect_ratio, projection=projection)

T = tycho2('tyc2index.npy', 'tyc2.npy', 'tyc2sup.npy')


fov_radians = np.radians(fov_degrees)

LM = 5
factor = 20

regions = T.regions_within_radius(center_RADEC, radius)
RAs, DECs, mags = T.stars_in_regions(regions, LM=LM)

xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
image_xy = coord.xyz_to_imagexy(*xyz, rotation=angle)

X, Y = coord.imagexy_to_pixelXY(image_xy, resolution, pixel_scale=zoom)

X_within = np.logical_and(X >= 0, X < resolution[0])
Y_within = np.logical_and(Y >= 0, Y < resolution[1])
XY_within = np.logical_and(X_within, Y_within)

X = X[XY_within]
Y = Y[XY_within]
mags = mags[XY_within]

plt.figure(1)
plt.clf()

plt.imshow(grayscale_data, cmap='gray')

stars = extract_stars(grayscale_data)
stars.sort(order='FLUX')

stars = stars[-len(mags):]

mag_sizes = (LM-mags)**2.5/15+.3

min_flux = stars['FLUX'].min()
flux_sizes = (stars['FLUX']-min_flux)/8/15+.3

plt.scatter(stars['X']-1, stars['Y']-1, 100, marker='o', linewidth=flux_sizes, facecolors='none', edgecolors='lime')
plt.scatter(X, Y, 100, linewidth=mag_sizes, marker='o', facecolors='none', edgecolors='red')

from icp import icp_metric

metric, dists, inds = icp_metric(stars, (X, Y), True)

for i,star in enumerate(stars):
    xline = [star['X'], X[inds[i]]]
    yline = [star['Y'], Y[inds[i]]]
    plt.plot(xline, yline, '-', color='yellow')