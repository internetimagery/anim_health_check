# Fix KEy doubleups

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

class DoubleUp_Check(base.Base_Check):
    """ Check for doubleups """
    def __init__(s):
        s.label = "Key Double-ups."
        s.description = """
Checks for keys occupying the same frame.

The fix will place a keyframe on the next frame if possible to preserve the animation, and remove the double-up key.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(list)
        for attr, keys in sel.iteritems():
            if 1 < len(keys): # Can't double up without two or more keys
                for k1, k2 in shift(keys, 2):
                    if k1[0] < (k2[0] + 0.05): # 0.05 threshold
                        found[attr].append(k2)
        return found

    def fix(s, sel):
        """ Remove double up keys preserving animation """
        for attr, keys in sel.iteritems():
            for time, value in keys:
                prev = cmds.findKeyframe(attr, t=(time, time), which="previous")
                print prev
                nxt_frame = int(time) + 1
                if not cmds.keyframe(attr, q=True, t=(nxt_frame,nxt_frame)):
                    cmds.setKeyframe(attr, t=nxt_frame)
                cmds.cutKey(attr, t=(time,time), cl=True)
		print 'Doubleups Deteted.'
