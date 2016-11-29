import viz

from omnistereo_camera_rig import *
from ortho_textured_camera import *
from animation_path_loader import *
from texture_saver import *

class OmnistereoFrameRecorder:
	'''Records a sequence omnistereo image frames. 
	The viewpoint transformation can be animated by handing an animation path'''
	
	## constructor
	def __init__(self, omnistereo_cam = None, frame_rate = 30, pixel_width = 4320, out_name = "", view_animation_file = "", animation_paths = [], mono = False):
		# name used for prefixing generated resource paths/files
		self._name = out_name
		if len(self._name) == 0:
			self._name = "omnistereo_panorama"
		
		# the omnistereo camera rig used for the recording process
		self._cam = omnistereo_cam
		if self._cam == None:
			self._initDefaultCamera(mono)
			
		# the orthogonal camera setup to record the stitched omnistereo image
		self._capture = None
		self._initCapture(pixel_width)
		
		# animation paths that will be animated in a way that fits the set frame rate for the recording
		self._animation_paths = animation_paths
		if len(view_animation_file) > 0:
			self._initViewAnimation(view_animation_file)
			
		# texture saver that will save the capture
		self._saver = TextureSaver(
			render_node = self._capture,
			out_name = self._name,
			frame_rate = frame_rate,
			animation_paths = self._animation_paths
		)
				
		# reference to event function called each frame
		vizact.onupdate(2, self._onUpdate)
		
	def getCamera(self):
		''' Returns the OmnistereoCameraRig of this instance. '''
		return self._cam
		
	def _onUpdate(self):
		"""function called each frame"""
		if self._saver.isRunning():
			self._saver.printStatus()
	
	def _initDefaultCamera(self, mono):
		"""helper function to initialize a default OmnistereoCameraRig, in case none was given"""
		if mono:
			self._cam = OmnistereoCameraRig(horizontal_samples = 200, vertical_samples = 2, eye_distance = 0.0, mono = True)
		else:
			self._cam = OmnistereoCameraRig(horizontal_samples = 200, vertical_samples = 2, eye_distance = 0.065)
		self._cam.setPosition(0.0,1.8,0.0)
		
	def _initCapture(self, pixel_width):
		"""helper function to initialize the OrthoTexturedCamera that captures the stitched omnistereo image"""
		if self._cam.isMono():
			self._capture = OrthoTexturedCamera(aspect = 2, width = pixel_width)
		else:
			self._capture = OrthoTexturedCamera(aspect = 1, width = pixel_width)
		link = viz.link(self._cam, self._capture)
		link.preTrans([0, 0, -0.1])
		self._cam.init(self._capture.getCamera())
		
	def _initViewAnimation(self, animation_name):
		"""helper function to load and initialize the view point animation of the omnistereo rig"""
		loader = AnimationPathLoader(file_name = animation_name)
		path = loader.getAnimationPath()
		viz.link(path, self._cam)
		self._animation_paths.append(path)
		
if __name__ == '__main__':
	import vizfx
	
	viz.setMultiSample(4)

	viz.go()

	cam = vizcam.WalkNavigate()
	
	piazza = viz.addChild("piazza.osgb")
	
	dude = viz.add('vcc_male.cfg') 
	dude.state(3)
	dude.setPosition(0,0,3)
	
	c = viz.addGroup()
	c.setPosition(0.0,0.8,1.5)
	ball = viz.addChild("basketball.osgb")
	ball.setParent(c)
	ball.setPosition(0.0,0.0,1.5)
	viz.link(c, ball)

	def timed_update():
		euler = c.getEuler()
		c.setEuler(euler[0] + 0.5, euler[1], euler[2])

	vizact.ontimer(0.01,timed_update)

	omni_rec = OmnistereoFrameRecorder(view_animation_file = "", mono = True, pixel_width = 1080)