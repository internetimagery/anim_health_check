import maya.cmds as cmds
#fix keys that fall between frames, but maintain peaks and holds

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Keys between frames.'
		self.description = """
Checks for keys that fall between frames. ie: frame 4.32 instead of frame 4.

The fix will put keys on whole frames.
"""

	def search(self, obj, attr, keys):
		for k in keys:
			if k%1:
				self.sel[obj] = self.sel.get(obj,{})
				self.sel[obj][attr] = self.sel[obj].get(attr,[])
				self.sel[obj][attr].append(k)

	def fix(self):
		for o in self.sel:
			for at in self.sel[o]:
				for k in self.sel[o][at]:
					if k%1 > 0.5:
						pref = int(k)+1
						alt = int(k)
					else:
						pref = int(k)
						alt = int(k)+1
					if cmds.keyframe(o, at=at, t=(pref,pref), q=True, kc=True ): #is there a frame already there?
						if cmds.keyframe(o, at=at, t=(alt,alt), q=True, kc=True ): #is there a frame on other side?
							if self.isPeak(o,at,k): #if peak, override frame with peak
								cmds.cutKey(o,at=at,t=(pref,pref),cl=True)
								cmds.keyframe(o,at=at,t=(k,k),tc=pref,a=True)
							else:
								cmds.cutKey(o,at=at,t=(k,k),cl=True)
						else:
							if self.isPeak(o,at,k): #if peak, override frame with peak
								cmds.keyframe(o,at=at,t=(k,k),tc=alt,a=True)
							else:
								cmds.setKeyframe(o,at=at,t=alt,i=True) #set key on opposite side to preserve animation
								cmds.cutKey(o,at=at,t=(k,k),cl=True)
					else:
						cmds.keyframe(o,at=at,t=(k,k),tc=pref,a=True)
		print 'Moved and or Removed keys on part frames.'

	def isPeak(self, o, at , key): #is this key a peak?
		prev = cmds.findKeyframe(o,at=at,t=(key,key),w='previous')
		next = cmds.findKeyframe(o,at=at,t=(key,key),w='next')
		v1 = cmds.keyframe(o,at=at,t=(prev,prev),q=True,vc=True)
		v2 = cmds.keyframe(o,at=at,t=(key,key),q=True,vc=True)
		v3 = cmds.keyframe(o,at=at,t=(next,next),q=True,vc=True)
		if (v2 >= v1 and v2 >= v3) or (v2 <= v1 and v2 <= v3):
			return True
		return False


