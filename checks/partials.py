# Fix Keys between frames
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

import functools
import collections
import maya.cmds as cmds

class Partial_Key_Check(object):
    """ Check for keys falling between frames """
    def __init__(s):
        s.label = "Keys between frames."
        s.description = """
Checks for keys that fall between frames. ie: frame 4.32 instead of frame 4.

The fix will put keys on whole frames.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(collections.OrderedDict)
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                if time % 1:
                    found[curve][time] = value
        return found

    def is_peak(s, curve, time, value):
        """ Test if keyframe is a peak """
        prev = cmds.findKeyframe(curve, t=(time,time), which='previous')
        next_ = cmds.findKeyframe(curve, t=(time,time), which="next")

        if prev == time or next_ == time: return True

        val1 = cmds.keyframe(curve, t=(prev,prev), q=True, vc=True)
        val2 = cmds.keyframe(curve, t=(next_,next_), q=True, vc=True)

        if (value >= val1 and value >= val2) or (value <= val1 and value <= val2):
            return True
        return False

    def fix(s, sel):
        """ Place keys on whole frames """
        delete = functools.partial(cmds.cutKey, cl=True) # Delete keyframe
        num_keys = functools.partial(cmds.keyframe, q=True, kc=True)
        move = functools.partial(cmds.keyframe, a=True)
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                if time % 1 > 0.5: # Which side do we favour?
                    alt = int(time)
                    pref = alt + 1 # Preferred time
                else:
                    pref = int(time)
                    alt = pref + 1
                is_peak = s.is_peak(curve, time, value) # Check if frame is a peak
                if num_keys(curve, t=(pref,pref)): # Check for keyframe on one side
                    if num_keys(curve, t=(alt, alt)): # Check the other side
                        if is_peak: # If we are a peak, override preferred frame
                            delete(curve, t=(pref,pref))
                            move(curve, t=(time,time), tc=pref) # Move key over
                        else:
                            delete(curve, t=(time,time)) # Not a peak, nothing special. Delete
                    else:
                        if is_peak:
                            move(curve, t=(time,time), tc=alt) # Move to alternate location
                        else:
                            cmds.setKeyframe(curve, t=alt, i=True) # Set keyframe maintaining curve
                            delete(curve, t=(time,time))
                else:
                    move(curve, t=(time,time), tc=pref)
        print "Moved or Removed keys between frames."
