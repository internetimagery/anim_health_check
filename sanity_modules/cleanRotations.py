import maya.cmds as cmds
#fix euler issues

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

#rotation angles. calculate ammount of rotation on all three channels. ensure rotation order is set with rotation ammount in mind

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Clean Rotations.'
		self.description = """
Checks for gimbal pops in rotation channels. Will only work if you've got animation on all three rotation channels and have them in the selection.

The fix runs a euler filter on the channels.
"""
		self.temp = {} #holding zone for selection
		self.rot = ['rotateX','rotateY','rotateZ']

	def search(self, obj, attr, keys):
		self.temp[obj] = self.temp.get(obj,{})
		if attr in self.rot:
			self.temp[obj][attr] = keys
		if len(self.temp[obj]) == 3: #only if 3 channels are there can we work on it
			start = max(self.temp[obj][self.rot[0]][0],self.temp[obj][self.rot[1]][0],self.temp[obj][self.rot[2]][0])
			end = min(self.temp[obj][self.rot[0]][-1],self.temp[obj][self.rot[1]][-1],self.temp[obj][self.rot[2]][-1])
			if start < end:
				if start%1:
					start = int(start)+1
				end = int(end)
				keyrange = end-start
				if keyrange > 1:
					for l in range(keyrange):
						l = start+l
						r=l+1
						check = {}
						for at in self.rot:
							v1 = cmds.keyframe(obj,at=at,t=(l,l),q=True,ev=True)[0]
							v2 = cmds.keyframe(obj,at=at,t=(r,r),q=True,ev=True)[0]
							diff = v2-v1
							if -90 > diff or diff > 90:
								check[at] = check.get(at,[])
								check[at].append(l)
								check[at].append(r)
						if len(check) > 1:
							self.sel[obj] = self.sel.get(obj, {})
							for at in check:
								self.sel[obj][at] = self.sel[obj].get(at, [])
								self.sel[obj][at].append(check[at][0])
								self.sel[obj][at].append(check[at][1])
					if self.sel and self.sel[obj]:
						for o in self.sel:
							for at in self.sel[o]:
								self.sel[o][at] = sorted(list(set(self.sel[o][at])))

	def fix(self):
		for o in self.sel:
			at = self.sel[o].keys()
			cmds.filterCurve((o+'.rx'),(o+'.ry'),(o+'.rz'))
		print 'Euler filtered.'
