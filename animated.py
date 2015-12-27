# Animated image
from __future__ import division

import os
import os.path
import time
import itertools
import threading
import traceback
import maya.cmds as cmds
import maya.utils as utils


class Animated_Image(object):
    """ Animated image I guess """
    def __init__(s):
        s.fps = 24
        s.gui = cmds.image()
        s.imgs = itertools.repeat("cube.png")
        s.block = threading.Semaphore()

        def go():
            while True:
                time.sleep(1 / s.fps)
                s.block.acquire()
                if not utils.executeInMainThreadWithResult(s.run):
                    break
        threading.Thread(target=go).start()

    def run(s):
        s.block.release()
        try:
            if cmds.image(s.gui, q=True, ex=True):
                cmds.image(s.gui, e=True, i=next(s.imgs))
                return True
        except:
            print traceback.format_exc()

    def add(s, images):
        s.imgs = itertools.cycle(images)
        return s


if __name__ == '__main__':
    img = os.path.realpath(r"D:\Documents\maya\2015-x64\scripts\anim_health_check\img")
    images = [os.path.join(img, a).replace("\\", "/") for a in os.listdir(img)]
    win = cmds.window()
    cmds.columnLayout()
    an = Animated_Image().add(images)
    cmds.showWindow()
