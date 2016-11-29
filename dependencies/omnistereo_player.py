import viz
import vizshape
import vizfx

from collections import Counter

class OmnistereoPlayer(viz.VizNode):
	'''
	 Used to display a captured omnistereo image or video.
	 The spherical video for each eye is mapped onto a sphere per eye.
	 Each sphere is only visible to an eye specific camera.
	 The capture of each eye can be retrieved by getting an output per eye.
	'''

	## constructor
	def __init__(self, footage_name = "", sphere_slices = 100, sphere_radius = 20, node = None, **kwargs):
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
	
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)

		# name of the file used for loading displayed data
		self._footage_name = footage_name
		self._footage = None
		self._footage_is_video = False
		self._initFootage()
		
		## right eye
		
		# node displaying the right eye video texture
		self._right_eye_sphere = vizshape.addSphere(radius = sphere_radius, slices = sphere_slices, stacks = sphere_slices, flipFaces = True)
		
		# effect used for the right eye
		self._right_eye_effect = viz.addEffect(self._getPanoramaMappingShaderCode())
		
		## left eye
		
		# node displaying the right eye video texture
		self._left_eye_sphere = vizshape.addSphere(radius = sphere_radius, slices = sphere_slices, stacks = sphere_slices, flipFaces = True)
		
		# effect used for the left eye
		self._left_eye_effect = viz.addEffect(self._getPanoramaMappingShaderCode())
		
		# initialize display spheres and render effect
		self._initPanoramas()
		
	def _getPanoramaMappingShaderCode(self):
		'''helper function returning a string to the shadercode used to map the panorama texture to the video sphere'''
		return """
			Effect {
				
				Texture2D StereoPanorama {
					unit 0
				}
				
				Int Eye {
					-1
				}
				
				Shader {
					BEGIN FragmentInit
					
					END
				
					BEGIN FinalColor

					uvStereoPanorama[1] = uvStereoPanorama[1]; // / 2.0;
					
					// right eye
					if(Eye > 0) {
						uvStereoPanorama[1] = uvStereoPanorama[1]; // + 0.5;
					}

					gl_FragColor = texture2D(StereoPanorama, uvStereoPanorama);
					
					END
				}
		"""
	
	def _initFootage(self):
		'''helper function to determine what kind of footage has been given (video/image)'''
		split = self._footage_name.split('.')
		if len(split) < 2:
			self._footage = None
			return
		
		file_type = split[-1]

		is_image = Counter(file_type) == Counter("jpg") or Counter(file_type) == Counter("jpeg") or Counter(file_type) == Counter("JPG") or Counter(file_type) == Counter("JPEG")
		if not is_image:
			is_image = is_image or Counter(file_type) == Counter("bmp") or Counter(file_type) == Counter("BMP")
			if not is_image:
				is_image = is_image or Counter(file_type) == Counter("png") or is_image or Counter(file_type) == Counter("PNG")
		
		self._footage_is_video = not is_image
		if self._footage_is_video:
			self._footage = viz.addVideo(self._footage_name)
			if not self._footage.valid() or self._footage.getDuration() == 0:
				self._footage = None
			self._footage.play()
			self._footage.loop()
		else:
			self._footage = viz.addTexture(self._footage_name)
			if not self._footage.valid() or self._footage.getSize()[0] == 0 or self._footage.getSize()[1] == 0:
				self._footage = None
		
	def _initAndApplyEffects(self):
		'''helper function that initializes the properties of right and left eye shader effects. Effects are applied on the respective node'''
		# right eye
		self._right_eye_sphere.disable(viz.CULL_FACE)
		self._right_eye_sphere.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
		self._right_eye_sphere.apply(self._right_eye_effect)
		if self._footage != None:
			self._right_eye_effect.setProperty("StereoPanorama", self._footage)
		self._right_eye_effect.setProperty("Eye", 1)
		
		# left eye
		self._left_eye_sphere.disable(viz.CULL_FACE)
		self._left_eye_sphere.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
		self._left_eye_sphere.apply(self._left_eye_effect)
		if self._footage != None:
			self._left_eye_effect.setProperty("StereoPanorama", self._footage)
		self._left_eye_effect.setProperty("Eye", -1)

	def _initPanoramas(self):
		'''helper function to initialize the output panorama spheres for left and right eye'''
		# right eye
		self._right_eye_sphere.renderToEye(viz.RIGHT_EYE)
		viz.link(self._node, self._right_eye_sphere)
		# left eye
		self._left_eye_sphere.renderToEye(viz.LEFT_EYE)
		viz.link(self._node, self._left_eye_sphere)
		# initializes and applies shader effect, so the panorama texture is mapped correctly
		self._initAndApplyEffects()
		
	def getFootageValid(self):
		'''returns whether the footage loaded upon initialization is valid'''
		return self._footage != None

if __name__ == '__main__':
	import vizcam
	import oculus
	
	viz.setMultiSample(4)
	viz.go()

	use_oculus = False
	
	cam = None
	hmd = None
	
	if use_oculus:
		hmd = oculus.Rift()
		viz.link(hmd.getSensor(), viz.MainView)
	else:
		cam = vizcam.WalkNavigate()

	player = OmnistereoPlayer('test.bmp', sphere_radius = 20.0, sphere_slices = 100)
	player.setPosition(viz.MainView.getPosition())
	
	# Change the background clear color to a shade of blue
	viz.clearcolor(viz.SLATE)