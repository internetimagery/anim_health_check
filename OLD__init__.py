from functools import partial
import smartselection as ss
import maya.cmds as cmds
import os as os
import sys

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

#REQUIRES SMART SELECTION SCRIPT

#TODO: need to select everything when

class AnimSanity(Exception):
	pass

directory = os.path.join(os.path.split(__file__)[0], 'sanity_modules')
scripts = [] #list of python files in directory
if os.path.isdir( directory ): #check directory exists
	sys.path.append( directory )
	for f in os.listdir( directory ):
		(filename, dot, filetype) = f.rpartition('.')
		if filename and filetype == 'py':
			scripts.append( filename )
else:
	raise AnimSanity('DANG SON... Folder "sanity_modules" does not exist in your script directory.')

class GUI(object):
	def __init__(self):
		self.modules = [] #build list of modules
		for module in scripts:
			mod = __import__(module)
			#reload(mod) #debug = update changes each load
			self.modules.append( mod.load() )

		self.GUI = {} #GUI components
		self.entry = {} # 0=image index 1=selection data!
		self.images = ['checkboxOff.png','checkboxOn.png','closeObject.png'] #images 0=not checked, 1=success, 2=failed

		self.GUI['window'] = cmds.window( title = 'Animation Sanity Check', rtf=True, s=False)
		self.GUI['layout1'] = {'self':cmds.columnLayout( adjustableColumn=True )}
		self.GUI['text1'] = cmds.text( l='Select objects you wish to check.', h=25)
		cmds.separator()
		self.GUI['text2'] = cmds.text(l='Check for...', h=35)
		self.GUI['layout2'] = {'self':cmds.rowColumnLayout( nc=5, cw=[(1,20),(3, 60),(4,60),(5,30)] )}
		self.addMods()
		cmds.setParent('..')
		self.GUI['button1'] = cmds.button(l='Check Animation', h=50, c=self.checkAnimation)
		cmds.setParent('..')
		cmds.showWindow( self.GUI['window'] )

	def addMods(self): #add mods into the GUI
		for mod in self.modules:
			p = self.GUI['layout2']['self']
			GUI = {}
			GUI['img'] = cmds.image(p=p, i= self.images[0] )
			GUI['txt'] = cmds.text(p=p, l=mod.label, al='left' )
			GUI['but1']= cmds.button(p=p, l= 'Show', en=False, c=partial(self.selectKeys, mod) )
			GUI['but2']= cmds.button(p=p, l= 'Fix it!', en=False, c=partial(self.fixKeys, mod) )
			GUI['but3']= cmds.button(p=p, l= '?', c=partial(self.helpmenu, mod))
			mod.GUI = GUI

	def helpmenu(self, mod, button):
		cmds.confirmDialog( title = mod.label, message = mod.description)

	def selectKeys(self, mod, *button): #select chosen keys
		try:
			mod.show()
		except AttributeError:
			if mod.sel:
				cmds.select(cl=True)
				for o in mod.sel:
					cmds.select(o, add=True)
					for at in mod.sel[o]:
						for k in mod.sel[o][at]:
							if cmds.keyframe(o, at=at, t=(k,k), kc=True, q=True ):
								cmds.selectKey( o, at=at, t=(k,k), add=True, k=True)

	def fixKeys(self, mod, *button):
		mod.fix()
		self.resetGUI()
		self.refreshSelection()
		self.checkAnimation()

	def refreshSelection(self):
		if self.selection:
			for o in self.selection:
				for at in self.selection[o]:
					self.selection[o][at] = cmds.keyframe(o,at=at,q=True)

	def resetGUI(self, *button): #reset all mods
		if button:
			self.selection = {}
		for mod in self.modules:
			cmds.image( mod.GUI['img'], e=True, i=self.images[0] )
			cmds.button( mod.GUI['but1'], e=True, en=False )
			cmds.button( mod.GUI['but2'], e=True, en=False )
			mod.sel = {}
			mod.__init__()
		cmds.button( self.GUI['button1'], l='Check Animation', e=True, c=self.checkAnimation )

	def activateGUI(self, mod): #activate mod
		if mod.sel:
			cmds.image( mod.GUI['img'], e=True, i=self.images[2] )
			cmds.button( mod.GUI['but1'], e=True, en=True )
			cmds.button( mod.GUI['but2'], e=True, en=True )
		else:
			cmds.image( mod.GUI['img'], e=True, i=self.images[1] )

	def loop(self, methods):
		if self.selection and methods:
			for o in self.selection:
				for at in self.selection[o]:
					for method in methods:
						method(o, at, self.selection[o][at])

	def checkAnimation(self, *button):
		if button:
			self.selection = ss.smartSelection(True).get()
		if self.selection:
			for mod in self.modules:
				self.loop([mod.search])
				self.activateGUI(mod)
				cmds.refresh( cv=True )
			cmds.button( self.GUI['button1'], l='Reset', e=True, c=self.resetGUI )
		else:
			cmds.confirmDialog(title='Hold up...', message='Select some objects with animations!')
