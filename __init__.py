# Run through chosen animation. Clean it up.

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
        cmds.button(l='Check Animation', h=50, c=Callback(s.filter_keys))
        cmds.showWindow(win)

    def help(s, module):
        """ Display Module Description """
        cmds.confirmDialog(t="What does this do?", m=module.description)

    def filter_keys(s):
        """ Run through all modules and filter keys """
        sel = selection.get_selection()
        for mod in s.modules:
            s.selection[mod] = filtered = mod.filter(sel)
            guis = s.modules[mod]
            for gui in guis["btn"]:
                cmds.button(gui, e=True, en=True if filtered else False)
            cmds.image(guis["img"], e=True, i=s.imgs[2 if filtered else 1])

    def highlight_issues(s, mod):
        """ Select all keys that cause issues """
        for attr, keys in s.selection.get(mod, {}).iteritems():
            cmds.select(attr.split(".")[0], add=True)
            for time, value in keys:
                cmds.selectKey(attr, t=(time,time), add=True, k=True)

    def fix_issues(s, mod):
        """ Attempt to fix issues """
        mod.fix(s.selection.get(mod, {}))

Main()
