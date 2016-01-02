# Contexturally make a selection.
# Created By Jason Dixon. http://internetimagery.com
#
# Wrap the outermost function calls in the Report class
# As a decorator or as a context manager on the outermost function calls
# For instance, decorate your Main() function,
# or any function that is called directly by a GUI
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
import itertools
import collections
import maya.mel as mel
import maya.cmds as cmds

def chunk(iterable, size, default=None):
    """ Iterate in chunks """
    return itertools.izip_longest(*[iter(iterable)]*size, fillvalue=default)

def get_channelbox_attributes(channel_box=functools.partial(cmds.channelBox, "mainChannelBox", q=True)):
    """ Get selections from the channel_box. Returns (obj, attr) """
    for obj, attr in itertools.product(channel_box(mol=True) or [], channel_box(sma=True) or []):
        if cmds.attributeQuery(attr, n=obj, ex=True):
            for curve in cmds.keyframe(obj, at=attr, q=True, n=True) or []:
                yield curve

def get_graph_attributes():
    """ Get channel selection from Graph. Returns (obj, attr) """
    for panel in cmds.getPanel(sty="graphEditor") or []:
        graph = cmds.selectionConnection(panel + "FromOutliner", q=True, obj=True) or []
        for attr in graph:
            if len(attr.split(".")) == 2:
                for curve in cmds.keyframe(attr, q=True, n=True) or []:
                    yield curve

def get_selected_keys(objs):
    """ Get a listing of selected keyframes. """
    for curve in cmds.keyframe(objs, q=True, n=True, sl=True) or []:
        keys = chunk(cmds.keyframe(curve, q=True, tc=True, vc=True, sl=True) or [], 2)
        yield curve, keys

def get_frame_range():
    """ Get selected frame range. Either the full time slider or something highlighted """
    slider = mel.eval("$tmp = $gPlayBackSlider")
    if cmds.timeControl(slider, q=True, rv=True):
        return cmds.timeControl(slider, q=True, ra=True)
    else:
        return cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)

def get_all_keys(objs):
    """ Given a list of objects. Get all attributes and keyframes """
    for curve in cmds.keyframe(objs, q=True, n=True) or []:
        keys = chunk(cmds.keyframe(curve, q=True, tc=True, vc=True) or [], 2)
        yield curve, keys

def get_selection():
    """
    Get current selection. Attributes to Keyframes
    Selection Priority:
        (1) Direct key selection
        (2) Graph Channel selection
        (3) Channelbox selection
        (4) All keyframes
    """
    sel = cmds.ls(sl=True, type="transform")
    if not sel: return {}
    # sel_keys = dict((a, collections.OrderedDict(b)) for a, b in get_selected_keys(sel))
    # if sel_keys: return sel_keys # If we have selected keyframes. This overrides all!

    min_, max_ = get_frame_range() # Get frame range
    all_keys = dict((a, collections.OrderedDict((c, d) for c, d in b if min_ <= c <= max_)) for a, b in get_all_keys(sel)) # And all keyframes

    filter_ = tuple(get_graph_attributes()) or tuple(get_channelbox_attributes()) # Get any other selections

    filtered_keys = dict((a, b) for a, b in all_keys.iteritems() if not filter_ or a in filter_ and b) # Filter our selection

    return filtered_keys

if __name__ == '__main__':
    print get_selection()
