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
            try:
                b.next()
            except StopIteration:
                pass
    return itertools.izip(*i)

# http://www.creativecrash.com/forums/mel/topics/euler-filter-algorithm#discussion_post_103750
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
        found = collections.defaultdict(collections.OrderedDict)
        if sel:
            cmds.undoInfo(openChunk=True)
            try:
                cmds.filterCurve(sel.keys()) # Try euler filter
                for curve, keys in sel.iteritems():
                    new_vals = dict((a, b) for a, b in chunk(cmds.keyframe(curve, q=True, tc=True, vc=True) or [], 2) if a in keys)
                    if keys != new_vals: # Check if anything changed
                        for (t1, v1), (t2, v2) in itertools.izip(keys.iteritems(), new_vals.iteritems()):
                            if v1 != v2:
                                found[curve][t1] = v1
            finally:
                cmds.undoInfo(closeChunk=True)
                cmds.undo()
        return found

    def fix(s, sel):
        """ Remove double up keys preserving animation """
        cmds.filterCurve(sel.keys())
        print "Euler filter applied"

if __name__ == '__main__':
    curves = cmds.keyframe("pCube1", q=True, n=True) or []
    data = dict((a, collections.OrderedDict(chunk(cmds.keyframe(a, q=True, tc=True, vc=True), 2))) for a in curves)
    mod = Euler_Check()
    data = mod.filter(data)
    mod.fix(data)
