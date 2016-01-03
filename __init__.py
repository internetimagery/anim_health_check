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

import os
import time
import checks
import report
import os.path
import itertools
import threading
import traceback
import selection
import collections
import maya.cmds as cmds
import maya.utils as utils

def get_images():
    root = os.path.join(os.path.dirname(__file__), "img")
    return dict((a, itertools.cycle(os.path.join(root, a, b).replace("\\", "/") for b in os.listdir(os.path.join(root, a)))) for a in os.listdir(root))

class EKG(object):
    """ EKG machine """
    def __init__(s):
        root = os.path.dirname(__file__)
        root_img = os.path.join(root, "img")
        neutral = itertools.cycle(os.path.join(root_img, "neutral", a).replace("\\", "/") for a in os.listdir(os.path.join(root_img, "neutral")))
        healthy = itertools.cycle(os.path.join(root_img, "healthy", a).replace("\\", "/") for a in os.listdir(os.path.join(root_img, "healthy")))
        dead = itertools.cycle(os.path.join(root_img, "dead", a).replace("\\", "/") for a in os.listdir(os.path.join(root_img, "dead")))
        s.imgs = itertools.izip(neutral, healthy, dead)
        s.img_index = 0 # Which image to display. 0 = neutral, 1 = healthy, 2 = dead
        s.gui = cmds.image(w=400, h=150)
        s.running = True
        s.block = threading.Semaphore()
        threading.Thread(target=s.run).start()

    def run(s):
        fps = 1.0 / 24
        while s.running:
            time.sleep(fps)
            s.block.acquire()
            utils.executeDeferred(s.change_image)

    def change_image(s):
        s.block.release()
        try:
            cmds.image(s.gui, e=True, i=next(s.imgs)[s.img_index])
        except:
            s.running = False


class Timer(object):
    """ Time the running of actions """
    verbose = True # Optional turn off timing
    def __init__(s, name): s.name = name
    def __enter__(s): s.start = time.time()
    def __exit__(s, *err):
        if s.verbose: print "%s...\t\tElapsed time: %sms." % (s.name, (time.time() - s.start) * 1000)

class Callback(object):
    """ Save variables in loops """
    def __init__(s, func, *args, **kwargs):
        s.__dict__.update(**locals())
    def __call__(s, *_): return s.func(*s.args, **s.kwargs)

class Main(object):
    """ Main GUI """
    imgs = ['checkboxOff.png','checkboxOn.png','closeObject.png'] #images 0=not checked, 1=success, 2=failed
    def __init__(s):
        with report.Report():
            s.modules = {} # Different Checks to perform
            s.selection = {}
            s._sel_monitor = cmds.ls(sl=True, type="transform")
            s._curve_monitor = []

            name = "animsanity"
            if cmds.window(name, q=True, ex=True):
                cmds.deleteUI(name)

            s.win = win = cmds.window(name, rtf=True, t="Animation Health Check!")
            cmds.columnLayout(adj=True)
            cmds.text(h=30, l="Select objects and attributes you wish to check")

            cmds.separator()
            s.EKG = EKG()
            cmds.separator()

            cmds.text(l="Check for...", h=35)

            col = cmds.columnLayout(adj=True)
            # Add MODS
            for mod in checks.modules:
                gui = {}
                cmds.rowLayout(nc=5, adj=2)
                gui["img"] = cmds.image(i=s.imgs[0])
                cmds.text(l=mod.label, al="left")
                gui["btn"] = [
                    cmds.button(l="show", en=False, w=60, c=Callback(s.highlight_issues, mod)),
                    cmds.button(l="Fix it!", en=False, w=60, c=Callback(s.fix_issues, mod))]
                cmds.button(l="?", w=30, c=Callback(s.help, mod))
                cmds.setParent(col)
                s.modules[mod] = gui

            cmds.setParent("..")
            s.go_btn = cmds.button(l='Check Animation', h=50, c=Callback(s.filter_keys))
            cmds.button(l="reset", h=30, c=Callback(s.reset_gui))
            cmds.showWindow(win)
            cmds.scriptJob(e=("SelectionChanged", s.monitor_selection_changes), p=win)

    def help(s, module):
        """ Display Module Description """
        cmds.confirmDialog(t="What does this do?", m=module.description)

    @report.Report()
    def monitor_selection_changes(s):
        """ Monitor Selection changes """
        sel = cmds.ls(sl=True, type="transform")
        if sel != s._sel_monitor:
            s._sel_monitor = sel
            s.reset_gui()

    @report.Report()
    def monitor_curve_changes(s, curve):
        """ Monitor changes to a curve """
        # Curve changed. This makes our data invalid.
        cmds.warning("Excuse me... %s changed. You must scan for issues again." % curve)
        cmds.scriptJob(ie=s.reset_gui, ro=True, p=s.win) # Cannot kill scriptjob while running

    def reset_gui(s):
        """ Set us back to a blank slate """
        for job in s._curve_monitor:
            if cmds.scriptJob(exists=job):
                cmds.scriptJob(kill=job)
        for mod, gui in s.modules.iteritems():
            cmds.image(gui["img"], e=True, i=s.imgs[0])
            for btn in gui["btn"]:
                cmds.button(btn, e=True, en=False)
        cmds.button(s.go_btn, e=True, en=True)
        s.EKG.img_index = 0

    @report.Report()
    def filter_keys(s):
        """ Run through all modules and filter keys """
        sel = selection.get_selection()
        if not sel: return cmds.confirmDialog(t="Whoops...", m="Nothing selected.")
        ok = True
        for mod in s.modules:
            with Timer("Checking %s" % mod.label):
                s.selection[mod] = filtered = mod.filter(sel, collections.defaultdict(collections.OrderedDict))
                guis = s.modules[mod]
                for gui in guis["btn"]:
                    cmds.button(gui, e=True, en=True if filtered else False)
                cmds.image(guis["img"], e=True, i=s.imgs[2 if filtered else 1])
                if filtered: ok = False # There are issues
        cmds.button(s.go_btn, e=True, en=False)
        for curve in sel: # Track changes to the curve
            s._curve_monitor.append(cmds.scriptJob(ac=("%s.a" % curve, Callback(s.monitor_curve_changes, curve)), p=s.win))
        s.EKG.img_index = 1 if ok else 2

    @report.Report()
    def highlight_issues(s, mod):
        """ Select all keys that cause issues """
        err = cmds.undoInfo(openChunk=True)
        try:
            select = collections.defaultdict(list) # Flip selection for efficiency
            for curve, keys in s.selection.get(mod, {}).iteritems():
                for t in keys:
                    select[t].append(curve)
            cmds.selectKey(clear=True)
            for t, curves in select.iteritems(): # Select keyframes
                cmds.selectKey(curves, t=(t,t), add=True, k=True)
        except Exception as err:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()

    @report.Report()
    def fix_issues(s, mod):
        """ Attempt to fix issues """
        s.reset_gui()
        err = cmds.undoInfo(openChunk=True)
        try:
            mod.fix(s.selection.get(mod, {}))
        except Exception as err:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            if err: cmds.undo()
        s.filter_keys()
