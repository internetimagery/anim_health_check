import maya.cmds as cmds
#turn stray stepped keys to auto

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Stepped Keys.'
		self.description = """
Checks for any stray stepped tangents.

The fix changes those tangents to AUTO.
Be aware of any stepped tangents you might actually want to keep. Such as turning on and off constraints.
"""

	def search(self, obj, attr, keys):
		for k in range(len(keys)):
		    if cmds.keyTangent( obj, at=attr, t=(keys[k],keys[k]), ott=True, q=True )[0] == 'step':
		    	self.sel[obj] = self.sel.get(obj, {})
		    	self.sel[obj][attr] = self.sel[obj].get( attr, [] )
		    	self.sel[obj][attr].append(keys[k])

	def fix(self):
		for o in self.sel:
			for at in self.sel[o]:
				for k in self.sel[o][at]:
					cmds.keyTangent( o, at=at, t=(k,k), ott='auto', e=True )
		print 'Stepped tangents converted to Auto.'
