import viz
import vizact
import os

from animation_path_player import *

from collections import Counter

class TextureSaver:
	'''saves a given texture on a frame to frame basis'''
	
	def __init__(self, render_node = None, out_name = "", frame_rate = 30, animation_paths = [], start = True):
		# texture to save out frame by frame
		self._render_node = render_node
		
		# name prefix for output folder and file
		self._name = ""
		self._initNameAndDir(out_name)			
		
		# frame rate for animation paths
		self._frame_rate = frame_rate

		# target frame_count (used for progress)
		self._target_frame_count = 0
		
		# animation path player to control playback of paths at given frame_rate to be animated while capturing
		self._animation_path_players = []
		self._initAnimationPathControl(animation_paths)
		self._initStopAllAnimations()
		
		# current frame being captured
		self._current_frame = 0
	
		# reference to event function called each frame
		self._on_update = vizact.onupdate(1, self._onUpdate)
		
		# progress in saving up to target_frame_count
		self._progress = -1

		# start time for saving action
		self._start_time = -1

		# flag that states if animation path capture is currently stopped
		self._stop = not start
		if not self._stop:
			self.start()
		
	def _onUpdate(self):
		"""function called each frame"""
		if self._stop:
			return
		elif self._render_node == None:
			self.stop()
		else:
			self._setAnimationTimes()
			self._saveTexture()
			self._computeProgress()
	
	def _saveTexture(self):
		"""saves the texture set"""
		if self._render_node == None:
			return
		if self._current_frame > self._target_frame_count:
			self.stop()
		
		postfix = str(self._current_frame)
		num_zeros = len(str(self._target_frame_count))
		
		while len(postfix) < num_zeros:
			postfix = "0" + postfix
		
		name = self._name + "/" + self._name + "_" + postfix + ".bmp"
		
		tex = self._render_node.getRenderTexture()
		if tex.valid() and tex.getSize()[0] != 0 and tex.getSize()[1] != 0:
			tex.save(name)
			self._current_frame += 1
	
	def _initStopAllAnimations(self):
		"""helper function to globally stop all animations so they can manually be set according to frame rate"""
		for node in viz.getNodeList():
			type_name = type(node).__name__

			if len(node.getAnimationNames()) > 0:
				node.setAnimationSpeed(0)
			
			if Counter(type_name) == Counter('VizAvatar'):
				node.setAnimationSpeed(0,0)
			elif Counter(type_name) == Counter('VizChild'):
				if len(node.getAnimationNames()) > 0:
					node.setAnimationSpeed(0)
			#else:
			#	if len(node.getAnimationNames()) > 0:
			#		node.setAnimationSpeed(0)
	
	def _setAnimationTimes(self):
		"""globally sets the time of all animations based on frame rate"""
		id_anim_map = self._getAnimationTimes()
		self._updateAnimationTimes(id_anim_map)
	
	def _getAnimationTimes(self):
		"""gets a map of all node ids, their respective animation times and a flag stating is the node is an avatar"""
		id_anim_map = {}

		for node in viz.getNodeList():
			type_name = type(node).__name__
			if Counter(type_name) == Counter('VizAvatar'):
				id_anim_map[node.id] = {"time" : node.getAnimationTime(0), "is_avatar" : True}
			elif Counter(type_name) != Counter('VizRenderNode'):
				if len(node.getAnimationNames()) > 0:
					id_anim_map[node.id] = {"time" : node.getAnimationTime(), "is_avatar" : False}
		
		return id_anim_map
	
	def _updateAnimationTimes(self, id_anim_map):
		"""sets the time of all animations contained by nodes in 'id_anim_map' based on frame rate"""
		EPSILON = 0.000001
		for node in viz.getNodeList():
			if node.id in id_anim_map:
				t1 = id_anim_map[node.id]["time"]
				if id_anim_map[node.id]["is_avatar"]:
					t2 = node.getAnimationTime(0)
					if abs(abs(t1) - abs(t2)) < EPSILON:
						self._updateAvatarAnimation(node)
				else:
					t2 = node.getAnimationTime()
					if abs(abs(t1) - abs(t2)) < EPSILON:
						self._updateNodeAnimation(node)
	
	def _updateAvatarAnimation(self, avatar):
		"""helper function to set the animation time on an avatar node based on frame rate"""
		time = avatar.getAnimationTime(0)
		time += 1/float(self._frame_rate)
		avatar.setAnimationTime(0,time)
	
	def _updateNodeAnimation(self, node):
		"""helper function to set the animation time on any node3d other than avatar based on frame rate"""
		if len(node.getAnimationNames()) > 0:
			time = node.getAnimationTime()
			time += 1/float(self._frame_rate)
			node.setAnimationTime(time)
		
	def _initAnimationPathControl(self, animation_paths):
		"""helper function for initialization of animation path players"""
		for path in animation_paths:
			path.setLoopMode(viz.OFF)
			self._animation_path_players.append(AnimationPathPlayer(
				frame_rate = self._frame_rate,
				path = path,
				start = False
			))
			frame_count = int(path.getDuration() * self._frame_rate) + 1 
			self._target_frame_count = max(self._target_frame_count, frame_count)

	def _initNameAndDir(self, name):
		"""helper function to initialize the output name"""
		self._name = name
		self._name.replace(".", "_")
		self._name.replace("/", "_")
		dir = os.getcwd() + '/' + self._name
		
		i = 2
		while os.path.isdir(dir):
			dir = os.getcwd() + '/' + self._name + "_" + str(i)
			i +=1
		
		if i != 2:
			self._name = self._name + "_" + str(i-1)
			
		os.makedirs(dir)
	
	def _computeProgress(self):
		"""computes the current progress"""
		if self._target_frame_count < 0:
			self._progress = -1
			return
		elif self._target_frame_count == 0:
			self._progress = 100
			return
			
		self._progress = self._current_frame / float(self._target_frame_count)
		self._progress = int(self._progress * 100)	
		
	def singleShot(self, file_name = ""):
		"""captures a single shot of the texture held by the render node.
		A file name (full path & extension) can be provide. If none is specified,
		name will be set to out_name set upon construction"""
		tex = self._render_node.getRenderTexture()
		if tex.valid() and tex.getSize()[0] != 0 and tex.getSize()[1] != 0:
			if len(file_name) > 0:
				tex.save(file_name)
			else:
				name = self._name + "/" + self._name + ".bmp"
				tex.save(name)			
	
	def start(self):
		"""starts frame export"""
		for player in self._animation_path_players:
			player.play()
		
		self._start_time = viz.getFrameTime()
		self._stop = False
		
	def stop(self):
		"""stops the frame export"""
		for player in self._animation_path_players:
			if player.isPlaying():
				player.stop()
				
		self._start_time = -1
		self._current_frame = 0
		self._stop = True
		
	def isRunning(self):
		"""returns whether the saver is currently running"""
		return not self._stop
	
	def getProgress(self):
		"""returns the progress for the save process. Returns -1 if no progress can be determined"""
		return self._progress

	def getRemainingEstimate(self):
		"""convenience function that returns an estimate for completing the save task"""
		if self._start_time == -1:
			return 0
		elif self._current_frame < 2:
			return -1
		
		remaining = viz.getFrameElapsed()
		remaining = remaining * (self._target_frame_count - self._current_frame)

		return remaining
	
	def secondsToTimeStr(self, num):
		"""converts number in seconds to formatted time string"""
		if num < 0:
			return "unknown"
		
		s = num
		m = 0
		h = 0
		d = 0
		
		if s > 60:
			temp = num/float(60)
			m = int(temp)
			s = temp*60 - m*60
		else:
			return str(int(s)) + " sec"
		
		if m > 60:
			temp = num/float(60)
			h = int(temp)
			m = temp*24 - h*60
		else:
			return str(int(m)) + " min " + str(int(s)) + " sec"
			
		if h > 24:
			temp = num/float(24)
			d = int(temp)
			h = temp*24 - d*24
		else:
			return str(int(h)) + " h " + str(int(m)) + " min " + str(int(s)) + " sec"
		
		return str(int(d)) + " days " + str(int(h)) + " h " + str(int(m)) + " min " + str(int(s)) + " sec"
		
	def printStatus(self):
		"""convenience function to print status of saving"""
		prog = str(self.getProgress())
		rem = self.secondsToTimeStr(self.getRemainingEstimate())
			
		print " > Progress " + prog + "%" + " (Remaining time " + rem + ")"
	
	
		