# Run through chosen animation. Clean it up.

import animsanity.checks as checks
import maya.cmds as cmds

class Main(object):
    """ Main GUI """
    def __init__(s):
        s.modules = modules = checks.modules
        s.imgs = imgs = ['checkboxOff.png','checkboxOn.png','closeObject.png'] #images 0=not checked, 1=success, 2=failed

        name = "animsanity"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        win = cmds.window(name, rtf=True, t="Animation Sanity!")
        cmds.columnLayout(adj=True)
        cmds.text(l="Select objects, attributes and / or keyframes you wish to check")
        cmds.separator()

        cmds.text(l="Check for...", h=35)

        row = cmds.rowColumnLayout(nc=5, rc=2, cw=((1,20),(3,60),(4,60),(5,30)))

        # Add MODS
        for mod in modules:
            cmds.image(i=imgs[0])
            cmds.text(l=mod.label, al="left")
            cmds.button(l="show", en=False, c="")
            cmds.button(l="Fix it!", en=False, c="")
            cmds.button(l="?", c="")
            cmds.setParent(row)

        cmds.setParent("..")
        cmds.showWindow(win)

Main()
