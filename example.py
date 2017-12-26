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

LM = 8
image_share = 0.65

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

fig = plt.figure(1)
fig.clf()

#(ax1, ax2) = fig.subplots(1, 2)
ax1 = fig.subplots(1,1)

fig2 = plt.figure(2)
fig2.clf()
ax2 = fig2.subplots(1,1)


ax1.imshow(grayscale_data, cmap='gray')

stars = extract_stars(grayscale_data)
stars.sort(order='FLUX')

# number of catalog stars <LM within frame
N_catalog = len(np.nonzero(XY_within)[0])
N_image = round(N_catalog*image_share)

print(N_catalog, N_image)

ostars = stars.copy()
ostars = ostars[-400:]

stars = stars[-N_image:]

dist = None
def fun(x):
    xy = transform(RAs, DECs, *x)
    #metric, distances, inds = icp_metric(stars, xy, True)
    #plt.plot(sorted(distances), '.-')
    #dist = distances
    metric = icp_metric(stars, xy)
    return metric

#plt.figure(2)
#plt.clf()
res = fmin(fun, x0)
#plt.plot(sorted(distances), '.-')



X, Y = transform(RAs, DECs, *res)

line_scale = 25
line_offset = .1

mag_sizes = (LM-mags)**2.5/line_scale+line_offset
min_flux = stars['FLUX'].min()
flux_sizes = (stars['FLUX']-min_flux)/8/line_scale+line_offset

catalog_color = 'yellow'
image_color = 'cyan'
star_alpha = 0
o_size = 40

ax1.scatter(stars['X'], stars['Y'], o_size, marker='o', linewidth=flux_sizes, facecolors='none', edgecolors=image_color, alpha=star_alpha)
ax1.scatter(X, Y, o_size*4, linewidth=mag_sizes, marker='o', facecolors='none', edgecolors=catalog_color, alpha=star_alpha)
#plt.scatter(X, Y, 100, linewidth=mag_sizes, marker='x', color='red')

from icp import icp_metric

metric, dists, inds = icp_metric(stars, (X, Y), True)

dist_limit = np.percentile(dists, 95)

ex = 10

for k,i in enumerate(inds):
    color = 'red' if dists[k] > dist_limit else 'lime'
    xline = np.array([stars['X'][k], X[i]])
    yline = np.array([stars['Y'][k], Y[i]])
    
    xmean = xline.mean()
    ymean = yline.mean()
    
    xline -= xmean
    yline -= ymean
    
    xline *= ex
    yline *= ex
    
    xline += xmean
    yline += ymean    
    
    ax1.plot(xline, yline, '-', color=color)
    
ax1.set_ylim(-1, resolution[1]+1)
ax1.set_xlim(-1, resolution[0]+1)
ax1.invert_yaxis()

ax2.plot(sorted(dists), '.-')
ax2.axhline(dist_limit)