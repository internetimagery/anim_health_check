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
import base
import itertools
import collections
import maya.cmds as cmds

def shift(iterable, size):
    """ iterate in groups ie [1,2,3] [2,3,4] """
    i = itertools.tee(iterable, size)
    for a, b in enumerate(i):
        for c in range(a):
            b.next()
    return itertools.izip(*i)

class Euler_Check(base.Base_Check):
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
        axis = re.compile(r"(rotate[XYZ]|r[xyz])$")
        rotations = dict((a, b) for a, b in sel.iteritems() if axis.search(a)) # Filter rotations
        if len(rotations) == 3: # Need all three axis to check rotations
            for attr, keys in rotations.iteritems():
                if 1 < len(keys): # Can't fix rotations with few keyframes
                    for time, value in keys:
                        next_frame = time + 1
                        value2 = cmds.keyframe(attr, t=(next_frame,next_frame), q=True, ev=True)[0]
                        diff = value2 - value
                        if -90 > diff or diff > 90: # Jumped too far!
                            found[attr].append((time, value))
        return found

    def fix(s, sel):
        """ Remove double up keys preserving animation """
        objs = set(a.split(".")[0] for a in sel)
        for o in objs:
            cmds.filterCurve((o+".rx"), (o+".ry"), (o+".rz"))
        print "Euler filter applied"
