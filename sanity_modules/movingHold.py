import maya.cmds as cmds
#fix stings of keys that all fall on flat tangents.

# Created by Jason Dixon 4/04/14
# http://internetimagery.com

class load(object):
	def __init__(self):
		self.sel = {}
		self.label = 'Moving Holds.'
		self.description = """
Checks for plateaus in the animation curve.

The fix deletes any redundant keys along the hold, and slopes the curve slightly.
"""

	def search(self, obj, attr, keys):
		val = cmds.keyframe( obj, at=attr, vc=True, q=True ) #grab values of keys
		if len(keys) > 2:
			for l in range((len(keys)-1)):
				r=l+1
				if val[l] == val[r]: #check if values are the same
					if cmds.keyTangent( obj, at=attr, q=True, oa=True, t=(keys[l],keys[l]))[0] == 0.0 and cmds.keyTangent( obj, at=attr, q=True, ia=True, t=(keys[r],keys[r]))[0] == 0.0:
						self.sel[obj] = self.sel.get(obj, {})
						self.sel[obj][attr] = self.sel[obj].get( attr, [] )
						self.sel[obj][attr].append(keys[l])
						self.sel[obj][attr].append(keys[r])
						self.sel[obj][attr] = sorted(list(set(self.sel[obj][attr])))

	def fix(self):
		for o in self.sel:
			for at in self.sel[o]:
				key = self.sel[o][at]
				segment = []
				for l in range((len(key)-1)):
					r=l+1
					vall = cmds.keyframe(o,at=at,q=True,t=(key[l],key[l]),vc=True)
					valr = cmds.keyframe(o,at=at,q=True,t=(key[r],key[r]),vc=True)
					if segment: #separate out keyframes into segments
						if (not vall == valr) or (not key[r] == cmds.findKeyframe(o,at=at,t=(key[l],key[l]),w='next')):
							segment.append( key[l] )
					else:
						segment.append( key[l] )
					if r == (len(key)-1):
						segment.append( key[r] )
					if len(segment) == 2: #we have a segment, now work it out
						cmds.cutKey( o, at=at, cl=True, t=((segment[0]+0.01),(segment[1]-0.01)) )
						if segment[0] == cmds.findKeyframe(o,at=at,w='first'):#is this the first segment?
						    t1 = cmds.findKeyframe(o,at=at,t=(segment[1],segment[1]),w='next')
						    t2 = segment[1]
						else: #otherwise move first key
						    t1 = cmds.findKeyframe(o,at=at,t=(segment[0],segment[0]),w='previous')
						    t2 = segment[0]
						val1 = cmds.keyframe(o,at=at,t=(t1,t1),vc=True,q=True)[0]
						val2 = cmds.keyframe(o,at=at,t=(t2,t2),vc=True,q=True)[0]
						cmds.keyframe(o,at=at,t=(t2,t2),e=True,vc=((val2-val1)*0.9+val1))
						cmds.keyTangent(o,at=at,t=(t2,t2),e=True,itt='auto',ott='auto')
						segment = []
		print 'Moved same value keyframes.'
