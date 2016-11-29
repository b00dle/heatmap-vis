import viz
import json

class AnimationPathLoader:
	"""can load JSON files containing animation path descriptions 
	   to create the corresponding animation path"""
	   
	## constructor
	def __init__(self, file_name = ""):
		# the name of the current file being parsed
		self._file_name = ""
		self.setFileName(file_name)

		# raw JSON data read
		self._raw = None

		# <animationpath> read extracted from json data
		self._animation_path = None		
		
		if len(self._file_name) != 0:
			self.load()
		
	def load(self):
		"""loads an animation path from a JSON serialized txt file, which is specified by the set file name"""
		if len(self._file_name) == 0:
			return
			
		with open(self._file_name) as data_file:
			self._raw = json.load(data_file)
		
		self._extractPathFromRaw()
			
	def setFileName(self, file_name):
		"""sets the file name for the file containing the animation path information"""
		self._file_name = file_name
		
		if not self._file_name.endswith(".txt"):
			self._file_name += ".txt"
	
	def getAnimationPath(self):
		"""returns the parsed animation path"""
		return self._animation_path
	
	def _extractPathFromRaw(self):
		"""helper function to setup animation path from JSON object"""
		if 'path' not in self._raw:
			self._animation_path = None
			return
		
		self._animation_path = viz.addAnimationPath()
		
		for record in self._raw['path']:
			self._addControlPointFromObject(record)
		
	def _addControlPointFromObject(self, obj):
		"""helper function to add a control point to the animation path"""		
		if "time" not in obj:
			return
		
		cp = viz.addControlPoint()
		
		pos_none = True
		if "position" in obj:
			if len(obj["position"]) == 3:
				cp.setPosition(obj["position"][0], obj["position"][1], obj["position"][2])
				pos_none = False
		
		rot_none = True
		if "rotation" in obj:
			if len(obj["rotation"]) == 3:
				cp.setEuler(obj["rotation"][0], obj["rotation"][1], obj["rotation"][2])
				rot_none = False
			
		scale_none = True
		if "scale" in obj:
			if len(obj["scale"]) == 3:
				cp.setScale(obj["scale"][0], obj["scale"][1], obj["scale"][2])
				scale_none = False
		
		if not (pos_none and rot_none and scale_none):
			self._animation_path.addControlPoint(obj["time"], cp)
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)

	viz.go()
	
	piazza = viz.addChild("piazza.osgb")

	vizcam.WalkNavigate()
	
	loader = AnimationPathLoader("test_animation.txt")
	
	path = loader.getAnimationPath()
	path.setLoopMode(viz.SWING)
	viz.link(path, viz.MainView)
	
	path.play()