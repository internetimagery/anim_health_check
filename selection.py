# Contexturally make a selection.

import itertools
import collections
import maya.cmds as cmds

tree = collections.defaultdict(lambda: tree())

def chunk(iterable, size, default=None):
    """ Iterate in chunks """
    return itertools.izip_longest(*[iter(iterable)]*size, fillvalue=default)

def get_objects():
    """ Return selected objects """
    for sel in cmds.ls(sl=True, type="transform") or []:
        yield sel

def get_attributes(obj):
    """ Given an object, return its animated attributes """
    for src, dest in chunk(cmds.listConnections(obj, c=True, p=True, type="animCurve") or [], 2):
        yield cmds.attributeName(src, l=True)

# attribute = cmds.listConnections( obj , source=True, type='animCurve')


# def get_selection():
#     """ Get current selection. Hierarchy of objects, attributes, keyframes """
#     objs = tree()
#     sel = cmds.ls(sl=True, type="transform") or []

if __name__ == '__main__':
    for obj in get_objects():
        print obj
        for attr in get_attributes(obj):
            print attr
