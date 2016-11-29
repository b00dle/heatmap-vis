from texture_projector import *

class ObserverProjector(TextureProjector):
	''' derived class implementing use of project_and_observe shader '''
	
	def __init__(
		self,
		texture, 
		observer_node = viz.MainView,
		view_node = None, 
		node = None,
		**kwargs
		):
		
		## shader setup
		# open the shaders, assuming it's relative to this code file
		vertCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'project_and_observe.vert'), 'r') as vertFile:
			vertCode = vertFile.read()
		fragCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'project_and_observe.frag'), 'r') as fragFile:
			fragCode = fragFile.read()

		shader = viz.addShader(frag=fragCode, vert=vertCode)
		
		# init BC
		TextureProjector.__init__(self, texture, view_node = view_node, shader = shader, node = node, **kwargs)
		
		# node used to track the observer
		self._observer_node = observer_node
		
		# Depth camera for capturing depth buffer
		# used for inverse shadow mapping.
		# To make sure projection only hits first surface along view direction.
		self._observer_depth_cam = viz.addRenderNode(inheritView = False)
		self._observer_depth_cam.setRenderTexture(
			viz.addRenderTexture(format = viz.TEX_DEPTH),
			buffer = viz.RENDER_DEPTH
		)
		self._observer_depth_cam.setProjectionMatrix(viz.Matrix.perspective(90.0,1.0,0.1,100.0))
		self._observer_depth_cam.setAutoClip(viz.OFF)
		viz.link(self._observer_node, self._observer_depth_cam)
		
		# depth texture captured by camera
		self._observer_depth_texture = self._observer_depth_cam.getRenderTexture(viz.RENDER_DEPTH)
		
		# setup & attach uniforms
		self._uniform_observer_proj = viz.addUniformMatrix('observer_ProjMat', self._depth_cam.getProjectionMatrix().get())
		self._uniform_observer_view = viz.addUniformMatrix('observer_ViewMat', toGL(self._observer_node.getMatrix(viz.ABS_GLOBAL)).get())
		self._uniform_observer_depth_texture = viz.addUniformInt('observerDepth', 4)
		
		self._shader.attach([
			self._uniform_observer_proj,
			self._uniform_observer_view, 
			self._uniform_observer_depth_texture
		])
		
	def update(self):
		''' see BC '''
		TextureProjector.update(self)
		self._uniform_observer_proj.set(self._observer_depth_cam.getProjectionMatrix().get())
		self._uniform_observer_view.set(toGL(self._observer_node.getMatrix(viz.ABS_GLOBAL)).get())	
		
	def affect(self, model):
		"""Allows a model (VizNode) to be specified as a target for texture projection.

		@model the VizNode object to texture.
		"""
		TextureProjector.affect(self, model)
		if self._observer_depth_texture != None:
			model.texture(self._observer_depth_texture, unit = 4)
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')
	
	projector = ObserverProjector(viz.addTexture('front.png'))
	projector.setPosition(viz.MainView.getPosition())
	projector.affect(piazza)
	
	def update():
		global projector
		projector.update()
		
	vizact.onupdate(0, update)