# Fix Key doubleups
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

import itertools
import maya.cmds as cmds

def shift(iterable, size):
    """ iterate in groups ie [1,2,3] [2,3,4] """
    i = itertools.tee(iterable, size)
    for a, b in enumerate(i):
        try:
            for c in range(a):
                b.next()
        except StopIteration:
            pass
    return itertools.izip(*i)

class DoubleUp_Check(object):
    """ Check for doubleups """
    def __init__(s):
        s.label = "Key Double-ups."
        s.description = """
Checks for keys occupying the same frame (ie extremely close together).

The fix will place a keyframe on the next frame if possible to preserve the animation, and remove the double-up key.
"""

    def filter(s, sel, found):
        """ Pull out relevant keys """
        for curve, keys in sel.iteritems():
            if 1 < len(keys): # Can't double up without two or more keys
                for (t1, v1), (t2, v2) in shift(keys.iteritems(), 2):
                    if t2 < (t1 + 0.05): # 0.05 threshold
                        found[curve][t2] = v2
        return found

    def fix(s, sel):
        """ Remove double up keys preserving animation """
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                prev = cmds.findKeyframe(curve, t=(time, time), which="previous")
                next_ = cmds.findKeyframe(curve, t=(time,time), which="next")
                if prev == time: # First frame
                    cmds.setKeyframe(curve, t=int(time), v=value)
                elif next_ == time: # Last frame
                    cmds.setKeyframe(curve, t=int(time) + 1, v=value)
                else:
                    nxt_frame = int(time) + 1
                    if not cmds.keyframe(curve, q=True, t=(nxt_frame,nxt_frame)):
                        cmds.setKeyframe(curve, t=nxt_frame, i=True)
                cmds.cutKey(curve, t=(time,time), cl=True)
		print 'Doubleups Cleared.'
