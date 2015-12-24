# Fix Moving holds
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
import collections
import maya.cmds as cmds

def shift(iterable, size):
    """ iterate in groups ie [1,2,3] [2,3,4] """
    i = itertools.tee(iterable, size)
    for a, b in enumerate(i):
        for c in range(a):
            b.next()
    return itertools.izip(*i)

class Movinghold_Check(object):
    """ Check for moving holds """
    def __init__(s):
        s.label = "Moving Holds."
        s.description = """
Checks for plateaus in the animation curve.

The fix deletes any redundant keys along the hold, and slopes the curve slightly.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(list)
        for curve, keys in sel.iteritems():
            if 2 < len(keys): # Need more than three keys to make a moving hold
                for k1, k2, k3 in shift(keys, 3):
                    if k1[1] == k2[1] and k2[1] == k3[1]:
                        found[curve].append(k2)
        return found

    def fix(s, sel):
        """ Remove redundant keys and angle curve slightly """
        scale = 0.1
        for curve, keys in sel.iteritems():
            segments = []
            segment = []
            all_keys = cmds.keyframe(curve, q=True, tc=True)
            all_vals = cmds.keyframe(curve, q=True, vc=True)
            if len(keys) == 1:
                segment.append(keys[0])
            else:
                for k1, k2 in shift(keys, 2):
                    next_ = all_keys.index(k1[0]) + 1
                    segment.append(k1)
                    if all_keys[next_] != k2[0]: # end segment
                        segments.append(segment)
                        segment = []
            segments.append(segment)
            for seg in segments:
                cmds.cutKey(curve, t=(seg[0][0], seg[-1][0]), cl=True) # Delete segment
                next_ = all_keys.index(seg[-1][0]) + 1
                next_frame = all_keys[next_] # Check next frame
                if next_frame == all_keys[-1]: # We are at the end of the curve
                    prev = all_keys.index(seg[0][0]) - 1
                    prev_frame = all_keys[prev]
                    if prev_frame == all_keys[0]: # We have cleared all keyframes
                        pass # We don't need to adjust the keyframes
                    else:
                        prev_val = all_vals[prev - 1]
                        new_val = (prev_val - seg[0][1]) * scale + seg[0][1]
                        cmds.keyframe(curve, t=(prev_frame, prev_frame), e=True, vc=new_val)
                else:
                    next_val = all_vals[next_ + 1]
                    new_val = (next_val - seg[0][1]) * scale + seg[0][1]
                    cmds.keyframe(curve, t=(next_frame, next_frame), e=True, vc=new_val)

#
# if __name__ == '__main__':
#     curve = "pCube1.rotateX"
#     raw_keys = iter(cmds.keyframe(curve, q=True, tc=True, vc=True))
#     keys = zip(raw_keys, raw_keys)
#     data = {curve: tuple(keys)}
#     check = Movinghold_Check()
#     filtered = check.filter(data)
#     check.fix(filtered)
