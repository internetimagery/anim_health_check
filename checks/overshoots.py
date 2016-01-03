# Fix Key Overshoots
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

from __future__ import division

import math
import itertools
import collections
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

def chunk(iterable, size, default=None):
    """ iterate in chunks ie [1,2,3] [4,5,6] """
    i = iter(iterable)
    return itertools.izip_longest(*[i]*size, fillvalue=default)

class Overshoot_Check(object):
    """ Check for overshoots """
    def __init__(s):
        s.label = "Overshoots."
        s.description = """
This checks for curves that go beyond any surrounding keys.

The fix places a key at the peak of the tangent or flattens the tangent.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(collections.OrderedDict)
        for curve, points in s.get_points(sel.keys()).iteritems():
            if 1 < len(points): # No overshoots if only one keyframe
                for (_, p1, p2), (p3, p4, _) in shift(points, 2):
                    if p4[0] in sel[curve] and p2: # Only check sections we're interested in
                        overshoots = s.get_overshoots(p1, p2, p3, p4)
                        if overshoots:
                            found[curve][p1[0]] = p1[1]
                            found[curve][p4[0]] = p4[1]
        return found

    def fix(s, sel):
        """ Remove overshoots preserving animation """
        answer = cmds.confirmDialog(
            t="How to proceed?",
            m="Would you like to key the overshoots or flatten them?",
            b=["Keyframe", "Flatten"])
        if answer == "Flatten":
            for curve, keys in sel.iteritems():
                for time, value in keys.iteritems():
                    cmds.keyTangent(curve, t=(time,time), itt="flat", ott="flat")
            print "Flattened overshoots"
        else:
            for curve, points in s.get_points(sel.keys()).iteritems():
                if 1 < len(points): # No overshoots if only one keyframe
                    for (_, p1, p2), (p3, p4, _) in shift(points, 2):
                        if p4[0] in sel[curve] and p2: # Only check sections we're interested in
                            for overshoot in s.get_overshoots(p1, p2, p3, p4):
                                cmds.setKeyframe(curve, t=overshoot[0], itt="flat", ott="flat")
            print "Keyed overshoots"

    def get_points(s, curves):
        """ Given Curves, get corresponding points """
        result = collections.defaultdict(list)
        tmp_curves = cmds.duplicate(curves) or [] # Make dupe
        try:
            cmds.keyTangent(tmp_curves, e=True, wt=True) # Ensure weighted tangents
            keys = chunk(cmds.keyframe(tmp_curves, q=True, iv=True, tc=True, vc=True) or [], 3)
            tangents = chunk(cmds.keyTangent(tmp_curves, q=True, ott=True, ia=True, oa=True, iw=True, ow=True) or [], 5)
            curve_iter = iter(curves)
            for (i, t, v), (ia, oa, iw, ow, ott) in itertools.izip(keys, tangents):
                if not i:
                    curve = next(curve_iter)
                iw = -iw # Reverse in weight
                ia, oa = math.radians(ia), math.radians(oa)
                p2 = t, v # Central point x, y
                p1 = math.cos(ia) * iw + t, math.sin(ia) * iw + v
                if ott == "step":
                    p3 = None
                else:
                    p3 = math.cos(oa) * ow + t, math.sin(oa) * ow + v
                result[curve].append((p1, p2, p3))
        finally:
            cmds.delete(tmp_curves)
        return result

    # Reference : http://stackoverflow.com/questions/2587751/an-algorithm-to-find-bounding-box-of-closed-bezier-curves
    def get_overshoots(s, p1, p2, p3, p4):
        """ Get keyframe overshoots """
        t_values = [] # Time values on curve
        points = [] # Points on curve

        x0, y0 = p1 # Pull out our axis
        x1, y1 = p2
        x2, y2 = p3
        x3, y3 = p4

        for i in range(2):
            if i:
                b = 6 * y0 - 12 * y1 + 6 * y2
                a = -3 * y0 + 9 * y1 - 9 * y2 + 3 * y3
                c = 3 * y1 - 3 * y0
            else:
                b = 6 * x0 - 12 * x1 + 6 * x2
                a = -3 * x0 + 9 * x1 -9 * x2 + 3 * x3
                c = 3 * x1 - 3 * x0
            if abs(a) < 0.0001: # Accuracy
                if abs(b) < 0.0001:
                    continue
                t = -c / b
                if 0 < t < 1:
                    t_values.append(t)
                continue
            b2ac = b * b - 4 * c * a
            if b2ac < 0:
                continue
            sqrtb2ac = math.sqrt(b2ac)
            t1 = (-b + sqrtb2ac) / (2 * a)
            if 0 < t1 < 1:
                t_values.append(t1)
            t2 = (-b - sqrtb2ac) / (2 * a)
            if 0 < t2 < 1:
                t_values.append(t2)

        num_values = len(t_values)
        while num_values:
            num_values -= 1
            t = t_values[num_values]
            mt = 1 - t
            x = (mt * mt * mt * x0) + (3 * mt * mt * t * x1) + (3 * mt * t * t * x2) + (t * t * t * x3)
            y = (mt * mt * mt * y0) + (3 * mt * mt * t * y1) + (3 * mt * t * t * y2) + (t * t * t * y3)
            if x0 + 0.5 < x < x3 - 0.5: # We don't want overshoots too close to edges
                if y0 + 0.001 <= y <= y3 - 0.001:
                    continue
                points.append((x, y))
        return points

if __name__ == '__main__':
    curves = cmds.keyframe(cmds.ls(sl=True, type="transform"), q=True, n=True)
    data = dict((a, dict(chunk(cmds.keyframe(a, q=True, tc=True, vc=True), 2))) for a in curves)
    check = Overshoot_Check()
    filtered = check.filter(data)
    check.fix(filtered)
