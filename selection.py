# Contexturally make a selection.

import functools
import itertools
import collections
import maya.mel as mel
import maya.cmds as cmds

tree = collections.defaultdict(lambda: tree())

def chunk(iterable, size, default=None):
    """ Iterate in chunks """
    return itertools.izip_longest(*[iter(iterable)]*size, fillvalue=default)

def is_animated(attr):
    """ Check if attribute is animated """
    return not not cmds.listConnections(attr, d=False, type="animCurve")

def get_objects():
    """ Return selected objects """
    for sel in cmds.ls(sl=True, type="transform") or []:
        yield sel

def get_attributes(obj):
    """ Given an object, return its attributes. Returns (obj, attr) """
    for obj, attr in itertools.izip(itertools.repeat(obj), cmds.listAttr(obj, k=True) or []):
        yield obj, attr

def get_keyframes(attr):
    """ Get keyframes from an attribute. Returns (time, value) """
    for time, value in chunk(cmds.keyframe(attr, q=True, tc=True, vc=True) or [], 2):
        yield time, value

def get_channelbox(channel_box=functools.partial(cmds.channelBox, "mainChannelBox", q=True)):
    """ Get selections from the channel_box. Returns (obj, attr) """
    for obj, attr in itertools.product(channel_box(mol=True), channel_box(sma=True)):
        if cmds.attributeQuery(attr, n=obj, ex=True):
            yield obj, attr

def get_graph():
    """ Get channel selection from Graph. Returns (obj, attr) """
    panel = cmds.getPanel(sty="graphEditor")[0] + "FromOutliner"
    graph = cmds.selectionConnection(panel, q=True, obj=True) or []
    for sel in graph:
        obj_attr = sel.split(".")
        if len(obj_attr) == 2:
            yield obj_attr

def get_selected_keys(obj):
    """ Get a listing of selected keyframes. Returns (obj, attr), (time, value) """
    for curve in cmds.keyframe(obj, q=True, n=True, sl=True) or []:
        attr = cmds.listConnections(curve, p=True, type="transform") or []
        keys = cmds.keyframe(curve, q=True, sl=True, tc=True, vc=True) or []
        for key in chunk(keys, 2):
            for at in attr:
                yield (at.split(".")), key

def get_frame_range():
    """ Get selected frame range. Either the full time slider or something highlighted """
    slider = mel.eval("$tmp = $gPlayBackSlider")
    if cmds.timeControl(slider, q=True, rv=True):
        return cmds.timeControl(slider, q=True, ra=True)
    else:
        return cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)


# def get_selection():
#     """ Get current selection. Hierarchy of objects, attributes, keyframes """
#     objs = tree()
#     sel = cmds.ls(sl=True, type="transform") or []

if __name__ == '__main__':
    print get_frame_range()
    # for obj in get_objects():
    #     for thing in get_selected_keys(obj):
    #         print thing
    #     for attr in get_attributes(obj):
    #         print attr
            # for key in get_keyframes(".".join((obj, attr))):
            #     print obj, attr, key
