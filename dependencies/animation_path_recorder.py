import viz
import vizact
import time
import json

class AnimationPathRecorder(viz.VizNode):
	"""records its position and rotation (and time captured)"""
	
	## constructor
	def __init__(self, start = True, node = None, **kwargs):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
	
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# container to save recorded data
		self._data = []
		
		# flag that states if animation path capture is currently stopped
		self._stop = not start
		
		# start time
		self._start_time = -1
		
		# average fps of the recording
		self._avg_fps = -1.0
		
		# reference to event function called each frame
		self._onUpdate = vizact.onupdate(0, self._onUpdate)
		
	def _onUpdate(self):
		"""function called each frame"""
		if not self._stop:
			self._capture()
		elif self._start_time != -1:
			self._start_time = -1
	
	def _capture(self):
		"""captures position, rotation and time stamp and appends to recorded"""
		
		# record based on elapsed time
		t = -1
		t = viz.getFrameTime()
		if self._start_time == -1:
			self._start_time = 0.0

		t -= self._start_time
		
		pos = self.getPosition()
		rot = self.getEuler()
		scale = self.getScale()
		self._data.append({"time" : t, "position" : pos, "rotation" : rot, "scale" : scale})
		
		self._updatAvgFps()
		
	def _updatAvgFps(self):
		"""updates the average fps of the recording"""
		if len(self._data) < 2:
			return

		fps = -1.0
		fps = 1 / (self._data[-1]["time"] - self._data[-2]["time"])
		if fps > 60:
			fps = 60.0
			
		if self._avg_fps < 0:
			self._avg_fps = fps
			return
		
		s = (len(self._data)-2)/float(len(self._data)-1)
		self._avg_fps = s * self._avg_fps + (1-s) * fps
	
	def getAverageFps(self):
		"""returns the average fps of the last recording (as floating point number)"""
		return self._avg_fps
	
	def stop(self):
		"""stops the recording"""
		self._start_time = -1
		self._stop = True
		
	def start(self):
		"""starts the recording"""
		self._stop = False
	
	def isRunning(self):
		"""returns if the recording is currently running"""
		return not self._stop
	
	def clear(self):
		"""clears all recorded data"""
		self._data = []
	
	def writeToFile(self, name, append = False):
		"""writes all recorded data into a Json serialized txt file"""
		if name.endswith(".txt"):
			name = str[:-4]
		
		if append:
			data_file = open(name + '.txt', 'a')
		else:
			data_file = open(name + '.txt', 'w')
		
		data_obj = {"path" : self._data} 
		
		data_file.write(json.dumps(data_obj)) 
		
		data_file.flush()
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)

	viz.go()
	
	cam = vizcam.WalkNavigate()
	
	piazza = viz.addChild("piazza.osgb")
	
	rec = AnimationPathRecorder(start = False)
	viz.link(viz.MainView, rec)
	
	def toggleRecord(rec): 
		if rec.isRunning():
			rec.stop()
			rec.writeToFile("test_animation")
			print "Animation path saved to test_animation.txt"
		else:
			rec.start()
			print "Animation path recording started."
		
	vizact.onkeydown('r', toggleRecord, rec)
	
	