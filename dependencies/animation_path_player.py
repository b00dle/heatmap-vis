import viz
import vizact

class AnimationPathPlayer:
	"""plays an animation path"""
	
	def __init__(self, path = None, playback_speed = 1.0, start = True):
		# path to play
		self._path = path
		
		# direction of playback (forward = 1 or backward = -1)
		self._playback_direction = 1
		
		# speed factor for playback (real time = 1.0)
		self._playback_speed = playback_speed
		
		# flag that states if animation path capture is currently stopped
		self._stop = not start
		
		# stores frame time of last update call
		self._last_frame_time = viz.getFrameTime()

		# reference to event function called each frame
		self._on_update = vizact.onupdate(0, self._onUpdate)
		
	def _onUpdate(self):
		"""function called each frame"""
		if not self._stop and self._path != None:
			self._continuePlay()
		elif self._path == None and not self._stop:
			self._stop = True
		
	def _continuePlay(self):
		"""plays the path with the given configuration"""
		if self._path == None:
			return
		
		# Calculate time stepping along animation path.
		# Set last frame time
		step = viz.getFrameTime() - self._last_frame_time
		self._last_frame_time = viz.getFrameTime()
		
		# Calculate new time from step and current time
		time = self._path.getTime()
		time += self._playback_direction * step * self._playback_speed
		
		# handle over stepped duration
		if time > self._path.getDuration():
			loop_mode = self._path.getLoopMode()
			if loop_mode == viz.LOOP:
				time = 0
			elif loop_mode == viz.SWING:
				self._playback_direction = -1
				time = self._path.getTime() + self._playback_direction * step
			else:
				self.stop()
				return
		elif time < 0.0:
			loop_mode = self._path.getLoopMode()
			if loop_mode == viz.LOOP:
				time = self._path.getDuration()
			elif loop_mode == viz.SWING:
				self._playback_direction = 1
				time = self._path.getTime() + self._playback_direction * step
			else:
				self.stop()
				return
		
		# set final time
		self._path.setTime(time);
	
	def isPlaying(self):
		"""returns if player is currently active"""
		return not self._stop
	
	def play(self):
		"""starts playing the attached path"""
		self._stop = False
		
	def stop(self):
		"""stops playing the attached path and resets it back to time 0"""
		if self._path != None:
			self._path.setTime(0.0)
		self._playback_direction = 1
		self._stop = True		