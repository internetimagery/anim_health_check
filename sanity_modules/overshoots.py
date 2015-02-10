import maya.cmds as cmds
import math as m
#place keys at the peaks of overshoots
import time as ti

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

#if two angles are going the same way (hump) is the midpoint always at the same place?
#if the two angles are opposite ways, is the midpoint in the same two locations?

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Overshoots.'
		self.description = """
This checks for curves that go beyond any surrounding keys.

The fix places a key at the peak of the tangent, unless the tangent is very close to flat.
In which case it will simply make the tangent flat.
"""

	def search(self, obj, attr, keys):
		if len(keys) > 1:
			val = cmds.keyframe( obj, at=attr, vc=True, q=True ) #grab values of keys
			for l in range((len(keys)-1)):
				r=l+1
				diff = int(keys[r]) - int(keys[l])
				if diff > 0:
					between = sorted([val[l],val[r]])
					for t in range(diff):
						t+=int(keys[l])+1
						test = cmds.keyframe(obj,at=attr,t=(t,t),q=True,ev=True)[0]
						if test < between[0] or test > between[1]:
							self.sel[obj] = self.sel.get(obj, {})
							self.sel[obj][attr] = self.sel[obj].get(attr, [])+[keys[l],keys[r]]
		try:
			self.sel[obj][attr] = sorted(list(set(self.sel[obj][attr])))
		except KeyError:
			pass
	def fix(self):
		for o in self.sel:
			for at in self.sel[o]:
				key = self.sel[o][at]
				for t2 in range(len(key)):
					t1 = t2-1
					if t2 and key[t2] == cmds.findKeyframe(o,at=at,t=(key[t1],key[t1]),w='next'):
						peaks = self.recursiveCheck(o,at,key[t1],key[t2],0.2)
						if peaks:
							for peak in peaks:
								if (int(key[t1])+1) > peak:
									cmds.keyTangent(o,at=at,t=(key[t1],key[t1]),e=True,oa=0.0,l=False)
								elif (int(key[t2])-1) < peak:
									cmds.keyTangent(o,at=at,t=(key[t2],key[t2]),e=True,ia=0.0,l=False)
								else:
									cmds.setKeyframe(o,at=at,t=(peak,peak),itt='flat',ott='flat',v=cmds.keyframe(o,at=at,t=(peak,peak),q=True,ev=True)[0])
		print 'Peaks keyed.'

	def recursiveCheck(self,o, at, t1, t2, stop, failsafe = 10):
		failsafe-=1
		if failsafe > 0:
			diff = t2 - t1
			if diff >= stop:
				step = diff*0.2
				last_check = None
				result = []
				for i in range(6):
					if i:
						t=t1+step*i
						lst = {'A': cmds.keyframe(o, at=at, t=((t-step),(t-step)), ev=True, q=True)[0],'B': cmds.keyframe(o, at=at, t=(t,t), ev=True, q=True)[0]}
						new_check = ''.join(sorted(lst,key=lst.get))
						if last_check and not last_check == new_check:
							result+= self.recursiveCheck(o,at,(t-step*2),t,stop,failsafe)
						last_check = new_check
				if result:
					return result
			else:
				return [((t2-t1)*0.5)+t1]
		return False
