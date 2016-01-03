# Remove Stepped Keys
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

class Stepped_Check(object):
    """ Check for stepped keys """
    def __init__(s):
        s.label = "Stepped Keys."
        s.description = """
Checks for any stray stepped tangents.

The fix changes those tangents to AUTO.
Be aware of any stepped tangents you might actually want to keep. Such as turning on and off constraints.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(collections.OrderedDict)
        curves = sel.keys()
        keys = iter(cmds.keyframe(curves, q=True, iv=True, tc=True, vc=True) or [])
        tangents = cmds.keyTangent(curves, q=True, ott=True) or []
        curves_iter = iter(curves)
        for i, t, v, ott in itertools.izip(keys, keys, keys, tangents):
            if not i:
                curve = next(curves_iter)
            if t in sel[curve] and ott == "step":
                found[curve][t] = v
        return found

    def fix(s, sel):
        """ Change Stepped keys to Auto tangents """
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                cmds.keyTangent(curve, e=True, t=(time,time), ott="auto")
        print "Stepped Keys Removed"

# if __name__ == '__main__':
#     import time, pprint
#     curves = cmds.keyframe(cmds.ls(sl=True, type="transform"), q=True, n=True)
#     data = dict((a, dict(chunk(cmds.keyframe(a, q=True, tc=True, vc=True), 2))) for a in curves)
#     check = Stepped_Check()
#     start = time.time()
#     filtered = check.filter(data)
#     took = time.time() - start
#     cmds.scriptJob(ie=lambda: pprint.pprint("Took: %sms" % (took * 1000)), ro=True)
