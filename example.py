# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 00:17:33 2017

@author: lauri.kangas
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from scipy.optimize import fmin

from tycho2 import tycho2
from projections import stereographic, unity, rectilinear
import coordinate_transformations as coord
import astrometry
from image_analysis import extract_stars

def transform(RAs, DECs, ra, dec, angle, scale):
    xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
    image_xy = coord.xyz_to_imagexy(*xyz, rotation=angle, projection=rectilinear)
    X, Y = coord.imagexy_to_pixelXY(image_xy, resolution, pixel_scale=scale)
    return X, Y

API_KEY = 'ailckcattnyvxxfu'
filename = 'images/otava2.jpg'

#solution, session = astrometry.solve(filename, api_key=API_KEY)
print(solution)
projection = rectilinear

image_data = mpimg.imread(filename)
grayscale_data = image_data.mean(axis=2)
resolution = np.array(image_data.shape[1::-1])
aspect_ratio = resolution[1]/resolution[0]

center_RADEC = np.radians([solution['ra'], solution['dec']])
angle = np.radians(-solution['orientation'])

scale = solution['pixscale']

radius = solution['radius']

fov_degrees, sensor_size = coord.radius2fov(radius, aspect_ratio, projection=projection)

T = tycho2('tyc2index.npy', 'tyc2.npy', 'tyc2sup.npy')


fov_radians = np.radians(fov_degrees)

LM = 7

#regions = T.regions_within_radius(center_RADEC, radius)
#RAs, DECs, mags = T.stars_in_regions(regions, LM=LM)

RAs, DECs, mags = T.stars_within_radius(center_RADEC, radius, LM)

# nämä korvattava funktiolla
#xyz = coord.rotate_RADEC(RAs, DECs, *center_RADEC)
#image_xy = coord.xyz_to_imagexy(*xyz, rotation=angle, projection=rectilinear)
#X, Y = coord.imagexy_to_pixelXY(image_xy, resolution, pixel_scale=zoom)

X, Y = transform(RAs, DECs, *center_RADEC, angle, scale)

X_within = np.logical_and(X >= 0, X < resolution[0])
Y_within = np.logical_and(Y >= 0, Y < resolution[1])
XY_within = np.logical_and(X_within, Y_within)

oX = X.copy()
oY = Y.copy()

#X = X[XY_within]
#Y = Y[XY_within]
#mags = mags[XY_within]

x0 = [*center_RADEC, angle, scale]


plt.figure(1)
plt.clf()

plt.imshow(grayscale_data, cmap='gray')

stars = extract_stars(grayscale_data)
stars.sort(order='FLUX')

# number of catalog stars <LM within frame
N_catalog = len(np.nonzero(XY_within)[0])
N_image = round(N_catalog*0.5)

print(N_catalog, N_image)

stars = stars[-N_image:]

def fun(x):
    xy = transform(RAs, DECs, *x)
    metric, distances, inds = icp_metric(stars, xy, True)
    plt.plot(sorted(distances), '.-')
    return metric

plt.figure(2)
res = fmin(fun, x0)

plt.figure(1)
X, Y = transform(RAs, DECs, *res)


mag_sizes = (LM-mags)**2.5/15+.3

min_flux = stars['FLUX'].min()
flux_sizes = (stars['FLUX']-min_flux)/8/15+.3

plt.scatter(stars['X'], stars['Y'], 50, marker='o', linewidth=flux_sizes, facecolors='none', edgecolors='lime')
plt.scatter(X, Y, 100, linewidth=mag_sizes, marker='o', facecolors='none', edgecolors='red')
#plt.scatter(X, Y, 100, linewidth=mag_sizes, marker='x', color='red')

from icp import icp_metric

metric, dists, inds = icp_metric(stars, (X, Y), True)

for k,i in enumerate(inds):
    xline = [stars['X'][k], X[i]]
    yline = [stars['Y'][k], Y[i]]
    plt.plot(xline, yline, '-', color='yellow')