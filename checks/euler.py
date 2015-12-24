# Fix Key Rotation Pops
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import re
import itertools
import collections
import maya.cmds as cmds

def chunk(iterable, size, default=None):
    """ Iterate in chunks """
    return itertools.izip_longest(*[iter(iterable)]*size, fillvalue=default)

def shift(iterable, size):
    """ iterate in groups ie [1,2,3] [2,3,4] """
    i = itertools.tee(iterable, size)
    for a, b in enumerate(i):
        for c in range(a):
            b.next()
    return itertools.izip(*i)

class Euler_Check(object):
    """ Check for rotation pops """
    def __init__(s):
        s.label = "Clean Rotations."
        s.description = """
Checks for gimbal pops in rotation channels. Will only work if you've got animation on all three rotation channels and have them in the selection.

The fix runs a euler filter on the channels.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(list)
        axis = re.compile(r"(.+)(rotate[XYZ]|r[xyz])$") # Filter rotation axis
        rotation_curves = collections.defaultdict(dict)
        for curve, keys in sel.iteritems(): # Divide up channels
            name = axis.search(curve)
            if name:
                rotation_curves[name.group(1)][curve] = keys
        for obj, curves in rotation_curves.iteritems():
            if 2 < len(curves): # We need all three channels
                for curve, keys in curves.iteritems():
                    for k1, k2 in shift(keys, 2):
                        middle = (k2[0] - k1[0]) * 0.5 + k1[0]
                        bounds = int(middle), int(middle)+1

                        gradient = [cmds.keyframe(curve, q=True, t=(a,a), ev=True)[0] for a in bounds]

                        if 90 < abs(gradient[1] - gradient[0]):
                            for c, k in curves.iteritems():
                                found[c] = k
        return found

    def fix(s, sel):
        """ Remove double up keys preserving animation """
        cmds.filterCurve(sel.keys())
        print "Euler filter applied"
