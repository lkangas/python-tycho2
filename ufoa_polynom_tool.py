# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 21:32:20 2018

@author: vostok
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def polynoms(k3, k2):
    return [k3, k2, 1-k3-k2, 0], \
            [k3, k2, -k3-k2, 0], \
            [k3, k2, -k3-k2], \
            [3*k3, 2*k2, 1-k3-k2]

def plot(ax, x, p, xlines=[], ylines=[], scale=1):
    l, = ax.plot(x, np.polyval(p, x)*scale)
    for xl in xlines:
        ax.axvline(xl, linestyle='--')
    for yl in ylines:
        ax.axhline(yl, linestyle='--')
        
    return l

def plot_all(k3, k2):
    pol, error, relative, der = polynoms(k3, k2)
    
    l0 = plot(ax0, x, pol, [0, 1], [0, 1])
    plot(ax0, x, [1, 0])
    l1 = plot(ax1, x, error, [0, 1], [0])
    l2 = plot(ax2, x, relative, [0, 1], [0], 100)
    l3 = plot(ax3, x, der, [0, 1], [1])

    return l0, l1, l2, l3
    

    
            

fig = plt.figure(1)
fig.clf()
axarr = fig.subplots(2,2)
ax0, ax1, ax2, ax3 = axarr.flatten()

ax1.set_ylim(-.5, .5)
ax2.set_ylim(-10, 10)
ax3.set_ylim(0, 2)

k3 = 0
k2 = -0

x = np.linspace(-.1, 1.1)

lines = plot_all(k3, k2)

pos3 = ax2.get_position()
pos2 = ax3.get_position()

slider_height = 0.03

slider3_ax = fig.add_axes([pos3.xmin, pos3.ymin-2.5*slider_height, pos3.width, slider_height])
slider3 = Slider(slider3_ax, 'k3', -1, 1, k3)

slider2_ax = fig.add_axes([pos2.xmin, pos2.ymin-2.5*slider_height, pos2.width, slider_height])
slider2 = Slider(slider2_ax, 'k2', -1, 1, k2)

def update(val):
    k3 = slider3.val
    k2 = slider2.val
    
    pol, error, relative, der = polynoms(k3, k2)
    
    lines[0].set_ydata(np.polyval(pol, x))
    lines[1].set_ydata(np.polyval(error, x))
    lines[2].set_ydata(np.polyval(relative, x)*100)
    lines[3].set_ydata(np.polyval(der, x))
    
    fig.canvas.draw_idle()

slider3.on_changed(update)
slider2.on_changed(update)

ax0.set_title('Radial correction function')
ax1.set_title('Error against p(r) = r')
ax2.set_title('Relative error (%)')
ax3.set_title('dp/dr')
fig.suptitle('UFOAnalyzer radial correction polynomial')


#axtesti = plt.axes()

