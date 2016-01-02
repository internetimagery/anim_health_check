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
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                if cmds.keyTangent(curve, q=True, t=(time,time), ott=True)[0] == "step":
                    found[curve][time] = value
        return found

    def fix(s, sel):
        """ Change Stepped keys to Auto tangents """
        for curve, keys in sel.iteritems():
            for time, value in keys.iteritems():
                cmds.keyTangent(curve, e=True, t=(time,time), ott="auto")
        print "Stepped Keys Removed"
