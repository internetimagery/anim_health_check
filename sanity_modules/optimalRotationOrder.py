import maya.cmds as cmds
import math as m
#pick an optimal rotation order

# Created by Jason Dixon 11/04/14
# http://internetimagery.com



class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Optimal Rotation Order.'
		self.description = """
!EXPERIMENTAL!

This check calculates the optimum rotation order.
You'll need animation on all three channels for this to check run.

The fix will attempt to convert the keys to the new rotation order.

IMPORTANT: The more keyframes you have on the channels, the better it will be converted. Sometimes Maya does like to flip out, so be sure to check your rotations if you perform this fix.
Sometimes a rotation order is used for artistic purposes. A common choice is ZXY for the root of the character. This may not always be the most optimal but it works. Ignore this check for these situations.
It is possible for there to be a few combinations that are optimal. This is evident by running the fix and still having the check fail. Don't sweat it. :)
"""
		self.temp = {} #holding zone for selection
		self.roo = {} #rotation orders

	def search(self, obj, attr, keys):
		self.temp[obj] = self.temp.get(obj,{})
		if attr in ['rotateX','rotateY','rotateZ']:
			self.temp[obj][attr] = keys
		if len(self.temp[obj]) == 3: #only if 3 channels are there we work on it
			totals = {} #running total of rotation values
			gimbal_cross = {} #running tally of gimbal crossings
			current_roo = cmds.xform( obj, q=True, roo=True )
			for at in self.temp[obj]:
				keyframes = len(self.temp[obj][at])
				totals[at[-1]] = 0
				if keyframes > 1:
					val = cmds.keyframe(obj,at=at,q=True,vc=True)
					for l in range((keyframes-1)):
						r=l+1
						totals[at[-1]] = totals.get(at[-1], 0)
						totals[at[-1]]+= self.num( (val[r] - val[l]) )
						gimbal_cross[at[-1]] = gimbal_cross.get(at[-1], 0)
						if self.gimbalCheck(val[l], val[r]): #check for gimbal crossing
							gimbal_cross[at[-1]]+=1

			totals_sorted = sorted(totals, key=totals.get) #smallest to biggest
			gimbal_sorted = sorted(gimbal_cross, key=gimbal_cross.get)
			last_axis = totals[totals_sorted[2]]
			middle_axis = totals[totals_sorted[1]]
			first_axis = totals[totals_sorted[0]]
			if last_axis-last_axis*0.2 < middle_axis < last_axis+last_axis*0.2: #much difference between axis?
				roo = current_roo
			else:
				roo = current_roo.replace( totals_sorted[2].lower(), '' ).upper()+totals_sorted[2]
			if not gimbal_cross[gimbal_sorted[2]] == 0 and not gimbal_cross[gimbal_sorted[0]] == gimbal_cross[gimbal_sorted[1]]: #some gimbal issues?
				gimbal_sorted.remove(roo[2].upper())
				roo = gimbal_sorted[1]+gimbal_sorted[0]+roo[2]

			roo = roo.lower()
			if not roo == current_roo: #rotation order is not optimal
				self.sel[obj] = self.sel.get(obj, {})
				self.sel[obj] = self.temp[obj]
				self.roo[obj] = roo

	def show(self):
		message = ''
		for o in self.sel:
			message+= o+'\ncurrent: '+cmds.xform(o, q=True, roo=True)+'\nproposed: '+self.roo[o]+'\n-----------'
		cmds.confirmDialog( title= 'Rotation Orders:', message = message)

	def gimbalCheck(self, val1, val2): #check if angles cross a multiple of 180, offset by 90 - ie: gimbal lock on the middle rotation-order channel
		if val1:
			mult = int(180.0 * round(val1/180.0))
		else:
			mult = 0
		if (val2 - val1) < 0:
			mult-=90
		else:
			mult+=90
		if val1 > mult > val2 or val1 < mult < val2:
			return True
		return False

	def num(self, n):
		if n < 0:
			return n *-1
		return n

	def fix(self):
		prevtime = cmds.currentTime(q=True)
		auto = AutoKey(False)
		master_keylist = []
		oldroo = {}
		time = TimeChange()
		for o in self.sel:
			oldroo[o] = cmds.xform(o, q=True, roo=True)
			for at in self.sel[o]:
				master_keylist+=self.sel[o][at]
		master_keylist = sorted(list(set(master_keylist)))

		for t in master_keylist:
			time.move(t)
			for o in self.sel:
				chan = cmds.keyframe(o, at='rotate', q=True, n=True, t=(t,t))
				if chan:
					for c in chan:
						at = c.rpartition('_')[-1]
						cmds.xform(o, p=True, roo=self.roo[o])
			 			cmds.setKeyframe(o, at=at, t=(t,t))
			 			cmds.xform(o, p=False, roo=oldroo[o])
		for o in self.sel:
			cmds.xform(o, p=False, roo=self.roo[o])
			cmds.filterCurve( (o+'.rx'), (o+'.ry'), (o+'.rz'))
			#cmds.filterCurve( (o+'.rx'), (o+'.ry'), (o+'.rz') , f='simplify', tol=0.05, tto=0.0)
		print 'Rotation orders changed.'

class AutoKey(object):
	def __init__(self, state):
		self.state = cmds.autoKeyframe(st=True,q=True)
		cmds.autoKeyframe(st=state)
	def __del__(self):
		cmds.autoKeyframe(st=self.state)

class TimeChange(object):
	def __init__(self):
		self.time = cmds.currentTime(q=True)
	def move(self, move, update=True):
		cmds.currentTime(move, u=update)
	def __del__(self):
		cmds.currentTime(self.time)
