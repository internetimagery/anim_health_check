import maya.cmds as cmds
#fix keys that are doubling up

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Key Double-ups.'
		self.description = """
Checks for keys occupying the same frame.

The fix will place a keyframe on the next frame if possible to preserve the animation, and remove the double-up key.
"""

	def search(self, obj, attr, keys):
		for l in range((len(keys)-1)):
			r=l+1
			if keys[r] < (keys[l]+0.05):
				self.sel[obj] = self.sel.get(obj, {})
				self.sel[obj][attr] = self.sel[obj].get( attr, [] )
				self.sel[obj][attr].append(keys[r])

	def fix(self):
		for o in self.sel:
			for at in self.sel[o]:
				for k in self.sel[o][at]:
					prev = cmds.findKeyframe( o, at=at, t=(k,k), which='previous')
					#v1 = cmds.keyframe(o,at=at,t=(prev,prev),q=True,vc=True)[0]
					#v2 = cmds.keyframe(o,at=at,t=(k,k),q=True,vc=True)[0]
					cmds.cutKey(o,at=at,t=(k,k),cl=True)
					#cmds.keyframe(o,at=at,t=(prev,prev),e=True,vc=( (v2-v1)*0.5+v1 ))
		print 'Doubleups Deteted.'
