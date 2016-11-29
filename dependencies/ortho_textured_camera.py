import viz
import vizcam

class OrthoTexturedCamera(viz.VizNode):
	"""tex quad that displays texture rendered by an orthographic camera setup"""
	
	## constructor
	def __init__(self, aspect = 2.0, width = 4320, near = 0.01, far = 100.0, node = None, renderTexQuad = False, outputPhysicalSize=None, **kwargs):
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
		
		# pixel sizes of the output render texture
		self._textureSize = [width, width / aspect]
		
		# normalized size of the texture
		if outputPhysicalSize == None:
			self._outputPhysicalSize = [1.0, 1.0/aspect]
		else:
			self._outputPhysicalSize = outputPhysicalSize
		
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# render mask, so the tex quad does not try to render itself
		self._mask = viz.addNodeMask()
		
		# camera used to render quad texture
		self._initCamera(near, far)
		
	def getSize(self):
		return self._outputPhysicalSize
	
	def _initCamera(self, near, far):
		"""initializes camera"""
		mat = viz.Matrix()
		#mat.makeOrtho(-self._outputPhysicalSize[0]/2.0, self._outputPhysicalSize[0]/2.0,-self._outputPhysicalSize[1]/2.0, self._outputPhysicalSize[1]/2.0, near, far)
		mat.makeOrtho(-self._outputPhysicalSize[0], self._outputPhysicalSize[0],-self._outputPhysicalSize[1], self._outputPhysicalSize[1], near, far)
		
		self._cam = viz.addRenderNode(size=self._textureSize)
		self._cam.setInheritView(False)
		self._cam.setMatrix(viz.Matrix())
		self._cam.setRenderTexture(viz.addRenderTexture())
		
		self._cam.setRenderLimit(viz.RENDER_LIMIT_FRAME)
		self._cam.setCullMask(self._mask)
		self._cam.setProjectionMatrix(mat)
		self._cam.enable(viz.CULL_FACE)
		self._cam.setAutoClip(False)
		viz.grab(self._node, self._cam)
	
	def getCamera(self):
		"""returns the render node rendering the image"""
		return self._cam
	
	def getCullMask(self):
		"""returns the cull mask of the camera"""
		return self._mask
		
	def getRenderTexture(self):
		"""returns the texture rendered into by the camera"""
		return self._cam.getRenderTexture()
	
	def getCamera(self):
		"""returns the <rendernode> that captures the renderTexture"""
		return self._cam
	
if __name__ == '__main__':
	viz.setMultiSample(4)

	viz.go()
	
	cam = vizcam.WalkNavigate()
	
	piazza = viz.addChild("piazza.osgb")
	
	tex_cam = OrthoTexturedCamera()
	tex_cam.setPosition(0.0,1.8,2.0)