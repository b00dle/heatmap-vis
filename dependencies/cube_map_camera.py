import viz
import vizcam
import vizact
import vizshape

class CubeMapCamera(viz.VizNode):
	''' class capturing a cube map from given position.
	Can save render texture to file. '''
	
	def __init__(self, resolution = [512,512], node = None, **kwargs):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# per side image resolution for cube map texture
		self._resolution = resolution
		
		# list of cameras capturing each side of the cube map
		self._cams = {  
			viz.POSITIVE_X : None,
			viz.NEGATIVE_X : None,
			viz.POSITIVE_Y : None,
			viz.NEGATIVE_Y : None,
			viz.POSITIVE_Z : None,
			viz.NEGATIVE_Z : None 
		}
		
		# cubemap texture
		self._textures =  {
			viz.POSITIVE_X : viz.addRenderTexture(),
			viz.NEGATIVE_X : viz.addRenderTexture(),
			viz.POSITIVE_Y : viz.addRenderTexture(),
			viz.NEGATIVE_Y : viz.addRenderTexture(),
			viz.POSITIVE_Z : viz.addRenderTexture(),
			viz.NEGATIVE_Z : viz.addRenderTexture() 
		}
		
		# initialize cube map cameras
		self._initCams()
		
	def _initCams(self):
		''' initializes cameras, which capture sides of cubemap '''
		# Rotation offset for each cubemap face
		CubeFacesEuler = {  viz.POSITIVE_X : [90,0,0],
							viz.NEGATIVE_X : [-90,0,0],
							viz.POSITIVE_Y : [0,-90,0],
							viz.NEGATIVE_Y : [0,90,0],
							viz.POSITIVE_Z : [0,0,0],
							viz.NEGATIVE_Z : [180,0,0] }
							
		# 90 degree FOV projection for each face
		CubeProjectionMatrix = viz.Matrix.perspective(90.0,1.0,0.1,100.0)
		
		# Create render node for each face of cubemap
		for face, euler in CubeFacesEuler.items():
			self._cams[face] = viz.addRenderNode(size = self._resolution, inheritView=False)
			self._cams[face].setRenderTexture(self._textures[face])
			self._cams[face].setEuler(euler)
			self._cams[face].setProjectionMatrix(CubeProjectionMatrix)
			self._cams[face].setRenderLimit(viz.RENDER_LIMIT_FRAME)
			viz.grab(self, self._cams[face])
			
	def getCubeMapCameras(self):
		''' Returns all cameras used for cube map capture '''
		return self._cams
		
	def getTextures(self):
		''' Returns render textures '''
		return self._textures
		
	def getResolution(self):
		''' Returns the resolution '''
		return self._resolution
		
	def setRenderLimit(self, limit):
		''' sets the render limit for all cube cameras. '''
		for face in self._cams:
			self._cams[face].setRenderLimit(limit)
			
	def setClearMask(self, mask):
		''' sets clear mask for all cube cameras. '''
		for face in self._cams:
			self._cams[face].setClearMask(mask)
			
	def saveAll(self, prefix = "cube", directory = ""):
		''' saves all cube map textures to .bmp file.
		"prefix" denotes the filename prefix for each file. 
		"directory" specifies the output directory. 
		Returns full path of files saved. '''
		if len(directory) > 0 and not directory.endswith('/'):
			directory += "/"
		
		paths = {
			viz.POSITIVE_X : directory + prefix + '_p_x.bmp',
			viz.NEGATIVE_X : directory + prefix + '_n_x.bmp',
			viz.POSITIVE_Y : directory + prefix + '_p_y.bmp',
			viz.NEGATIVE_Y : directory + prefix + '_n_y.bmp',
			viz.POSITIVE_Z : directory + prefix + '_p_z.bmp',
			viz.NEGATIVE_Z : directory + prefix + '_n_z.bmp'
		}
		
		for face in self._textures:
			self._textures[face].save(paths[face])
			
		return paths

if __name__ == '__main__':
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	# Center of cubemap
	CENTER = [0,1.8,3]

	# Cubemap resolution
	RESOLUTION = [512,512]

	# Use pivot camera
	vizcam.PivotNavigate(center=CENTER,distance=5)

	# Add environment
	viz.add('gallery.osgb')

	# Add logo spinning around cubemp
	logo = viz.add('logo.osgb')
	logo.setPosition([2,1,3])
	logo.setCenter([-2,0,0])
	logo.runAction(vizact.spin(0,1,0,90))

	# init cube map
	cube_cam = CubeMapCamera(resolution = RESOLUTION)
	cube_cam.setPosition(CENTER)

	def capture():
		global cube_cam
		cube_cam.saveAll("test")
		
	vizact.ontimer2(1.0, 0, capture)