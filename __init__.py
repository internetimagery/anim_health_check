# Run through chosen animation. Clean it up.
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

import animsanity.checks as checks
import animsanity.selection as selection
import maya.cmds as cmds

class Callback(object):
    """ Save variables in loops """
    def __init__(s, func, *args, **kwargs):
        s.__dict__.update(**locals())
    def __call__(s, *_): return s.func(*s.args, **s.kwargs)

class Main(object):
    """ Main GUI """
    def __init__(s):
        s.modules = {} # Different Checks to perform
        s.imgs = imgs = ['checkboxOff.png','checkboxOn.png','closeObject.png'] #images 0=not checked, 1=success, 2=failed
        s.selection = {}
        s.ready = True # Ready state
        s._sel_monitor = None

        name = "animsanity"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        win = cmds.window(name, rtf=True, t="Animation Sanity!")
        cmds.columnLayout(adj=True)
        cmds.text(l="Select objects, attributes and / or keyframes you wish to check")
        cmds.separator()

        cmds.text(l="Check for...", h=35)

        col = cmds.columnLayout(adj=True)
        # Add MODS
        for mod in checks.modules:
            gui = {}
            cmds.rowLayout(nc=5, adj=2)
            gui["img"] = cmds.image(i=imgs[0])
            cmds.text(l=mod.label, al="left")
            gui["btn"] = [
                cmds.button(l="show", en=False, w=60, c=Callback(s.highlight_issues, mod)),
                cmds.button(l="Fix it!", en=False, w=60, c=Callback(s.fix_issues, mod))]
            cmds.button(l="?", w=30, c=Callback(s.help, mod))
            cmds.setParent(col)
            s.modules[mod] = gui

        cmds.setParent("..")
        s.go_btn = cmds.button(l='Check Animation', h=50, c=Callback(s.filter_keys))
        cmds.showWindow(win)
        cmds.scriptJob(e=("SelectionChanged", s.monitor_selection), p=win)

    def help(s, module):
        """ Display Module Description """
        cmds.confirmDialog(t="What does this do?", m=module.description)

    def monitor_selection(s):
        """ Monitor Selection changes """
        sel = cmds.ls(sl=True, type="transform")
        if sel != s._sel_monitor:
            s._sel_monitor = sel
            print "selection changed"
            if not s.ready:
                s.reset_gui()

    def reset_gui(s):
        """ Set us back to a blank slate """
        for mod, gui in s.modules.iteritems():
            cmds.image(gui["img"], e=True, i=s.imgs[0])
            for btn in gui["btn"]:
                cmds.button(btn, e=True, en=False)
        cmds.button(s.go_btn, e=True, en=True)
        s.ready = True

    def filter_keys(s):
        """ Run through all modules and filter keys """
        sel = selection.get_selection()
        for mod in s.modules:
            s.selection[mod] = filtered = mod.filter(sel)
            guis = s.modules[mod]
            for gui in guis["btn"]:
                cmds.button(gui, e=True, en=True if filtered else False)
            cmds.image(guis["img"], e=True, i=s.imgs[2 if filtered else 1])
        cmds.button(s.go_btn, e=True, en=False)
        s.ready = False

    def highlight_issues(s, mod):
        """ Select all keys that cause issues """
        err = None
        cmds.undoInfo(openChunk=True)
        try:
            cmds.select(clear=True)
            for attr, keys in s.selection.get(mod, {}).iteritems():
                cmds.select(attr.split(".")[0], add=True)
                for time, value in keys:
                    cmds.selectKey(attr, t=(time,time), add=True, k=True)
        except Exception as err:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()

    def fix_issues(s, mod):
        """ Attempt to fix issues """
        err = cmds.undoInfo(openChunk=True)
        try:
            mod.fix(s.selection.get(mod, {}))
        except Exception as err:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()

Main()
