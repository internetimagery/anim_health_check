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

# import base
import math
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

The fix places a key at the peak of the tangent, unless the tangent is very close to flat.
In which case it will simply make the tangent flat.
"""

    def filter(s, sel):
        """ Pull out relevant keys """
        found = collections.defaultdict(list)
        for attr, keys in sel.iteritems():
            if 1 < len(keys): # Can't overshoot without two or more keys
                for k1, k2 in shift(s.get_keys(attr), 2): # Use different key capturing mechanism
                    if s.get_overshoots(k1[1], k1[2], k2[0], k2[1]):
                        found[attr].append(k1[1])
                        found[attr].append(k2[1])
        return found

    def fix(s, sel):
        """ Remove overshoots preserving animation """
        for attr, keys in sel.iteritems():
            for k1, k2 in chunk(keys, 2):
                pass

    def get_keys(s, attr):
        """ Given an attribute snag all relevant keyframe information """
        for curve in cmds.listConnections(attr, d=False, type="animCurve") or []:
            temp_curve = cmds.duplicate(curve)[0] # Create a temporary curve to not destroy animation
            try:
                cmds.keyTangent(temp_curve, e=True, wt=True) # Turn on weighted tangents
                keys = chunk(cmds.keyframe(temp_curve, q=True, tc=True, vc=True) or [], 2)
                tangents = chunk(cmds.keyTangent(temp_curve, q=True, ia=True, oa=True, iw=True, ow=True, wt=True, ott=True) or [], 5)
                for key, tangent in itertools.izip(keys, tangents):
                    tangent_type = tangent[0]
                    if tangent_type == "step":
                        pass # TODO: Do I need to worry about stepped tangents?
                    yield s.get_points(*key + tangent[1:])
            finally:
                cmds.delete(temp_curve)

    def get_points(s, time, value, in_angle, out_angle, in_weight, out_weight):
         """ Given details about a keyframe, pull out points. """
         in_weight = -in_weight # Reverse weight
         in_angle, out_angle = math.radians(in_angle), math.radians(out_angle)
         p2 = (time, value) # The point itself
         p1 = (math.cos(in_angle) * in_weight + time, math.sin(in_angle) * in_weight + value)
         p3 = (math.cos(out_angle) * out_weight + time, math.sin(out_angle) * out_weight + value)
         return p1, p2, p3

    # Credit : http://stackoverflow.com/questions/2587751/an-algorithm-to-find-bounding-box-of-closed-bezier-curves
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
            points.append((x, y))
        return points

attr = "pSphere1.translateX"
keys = chunk(cmds.keyframe(attr, q=True, tc=True, vc=True) or [], 2)
data = {attr: tuple(keys)}

check = Overshoot_Check()

print check.filter(data)



# http://stackoverflow.com/questions/2587751/an-algorithm-to-find-bounding-box-of-closed-bezier-curves

# obj = pmc.PyNode("pSphere1")
# attr = obj.translateX
# keys = pmc.keyframe(attr, q=True, tc=True, vc=True)
# tans = pmc.keyTangent(attr, q=True, ia=True, oa=True, iw=True, ow=True, wt=True)
# weighted = tans.pop(0)
#
# combined = (tuple(itertools.chain(a, b)) for a, b in itertools.izip(keys, chunk(tans, 4)))
#
# # duplicate -rr;select -r pSphere1_translateX1 ;
# working = pmc.duplicate(attr.connections(type="animCurve"), rr=True)[0]
#
# for k1, k2 in shift(combined, 2):
#
#     if "step" != pmc.keyTangent(attr, t=(k2[0],k2[0]), q=True, ott=True):
#
#         p1 = k1[:2]
#         p4 = k2[:2]
#
#         left_angle = math.radians(k1[3])
#         left_weight = k1[5]
#         right_angle = math.radians(k2[2])
#         right_weight = -k2[4]
#
#         p2 = [math.cos(left_angle) * left_weight + p1[0], math.sin(left_angle) * left_weight + p1[1]]
#         p3 = [math.cos(right_angle) * right_weight + p4[0], math.sin(right_angle) * right_weight + p4[1]]
#
#         peaks = getBoundsOfCurve(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1])
#
#         for peak in peaks:
#             if p1[1] < peak[1] < p2[1]:
#                 continue
#             pmc.setKeyframe(attr, t=peak[0], i=True)
