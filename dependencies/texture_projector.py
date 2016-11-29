import viz
import os
import vizshape
import vizact

def toGL(mat = viz.Matrix()):
	""" Converts a vizard matrix to a GL matrix. """
	temp_mat = viz.Matrix(mat)
	quat = temp_mat.getQuat()
	pos = temp_mat.getPosition()
	temp_mat.setPosition(pos[0], pos[1], -pos[2])
	temp_mat.setQuat(-quat[0], -quat[1], quat[2], quat[3])
	return temp_mat.inverse()

class TextureProjector(viz.VizNode):
	''' class providing projective texture effect '''
	
	def __init__(
		self,
		texture,
		projection_matrix = viz.Matrix.perspective(90.0,1.0,0.1,100.0),
		view_node = None,
		shader = None,
		node = None,
		**kwargs
		):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# set projected texture
		self._texture = texture
		if self._texture != None:
			self._texture.wrap(viz.WRAP_S, viz.CLAMP_TO_BORDER)
			self._texture.wrap(viz.WRAP_T, viz.CLAMP_TO_BORDER)
			
		# list of nodes affected by this projector
		self._affected_nodes = []
		
		# check if shader has been given
		self._shader = shader
		if self._shader == None:
			# open the shaders, assuming it's relative to this code file
			vertCode = ""
			with open(os.path.join(os.path.dirname(__file__), 'projective.vert'), 'r') as vertFile:
				vertCode = vertFile.read()
			fragCode = ""
			with open(os.path.join(os.path.dirname(__file__), 'projective.frag'), 'r') as fragFile:
				fragCode = fragFile.read()
				
			# add shader from code
			self._shader = viz.addShader(frag=fragCode, vert=vertCode)
		
		# set projection matrix
		self._projection_mat = projection_matrix
		
		# rendering view node
		# used to compute inverse view transform inside shader
		self._view_node = view_node
		if self._view_node == None:
			self._view_node = viz.MainView
		
		# Depth camera for capturing depth buffer
		# used for inverse shadow mapping.
		# To make sure projection only hits first surface along view direction.
		self._depth_cam = viz.addRenderNode(inheritView = False)
		self._depth_cam.drawOrder(100)
		self._depth_cam.setRenderTexture(
			viz.addRenderTexture(format = viz.TEX_DEPTH),
			buffer = viz.RENDER_DEPTH
		)
		self._depth_cam.setProjectionMatrix(self._projection_mat)
		self._depth_cam.setAutoClip(viz.OFF)
		viz.link(self, self._depth_cam)
		
		# depth texture captured by camera
		self._depth_texture = self._depth_cam.getRenderTexture(viz.RENDER_DEPTH)
		
		# add uniforms for shader and initialize with default values
		self._uniform_tex_view = viz.addUniformMatrix('tex_ViewMat', toGL(self.getMatrix()).get())
		self._uniform_tex_proj = viz.addUniformMatrix('tex_ProjMat', self._projection_mat.get())
		self._uniform_view_inverse = viz.addUniformMatrix('viewMatInverse', toGL(self._view_node.getMatrix().inverse()).get())
		self._uniform_proj_texture = viz.addUniformInt('projectionTex', 2)
		self._uniform_depth_texture = viz.addUniformInt('projectionDepth', 3)
		self._shader.attach([
			self._uniform_tex_view,
			self._uniform_tex_proj, 
			self._uniform_view_inverse, 
			self._uniform_proj_texture, 
			self._uniform_depth_texture
		])
		
	def update(self):
		''' Function called on update. Will set uniform values. '''
		self._uniform_tex_view.set(toGL(self.getMatrix(viz.ABS_GLOBAL)).get())
		self._uniform_tex_proj.set(self._projection_mat.get())
		self._uniform_view_inverse.set(toGL(self._view_node.getMatrix(viz.ABS_GLOBAL).inverse()).get())
	
	def setTexture(self, tex):
		''' Sets the texture of this projector '''
		if tex != None:
			for model in self._affected_nodes:
				model.texture(tex, unit = 2)
		if self._texture != None:
			self._texture.remove()
		self._texture = tex
		
	def getTexture(self):
		''' Gets the texture of this projector '''
		return self._texture
		
	def affect(self, model):
		"""Allows a model (VizNode) to be specified as a target for texture projection.

		@model the VizNode object to texture.
		"""
		if model not in self._affected_nodes:
			model.apply(self._shader)
			if self._texture != None:
				model.texture(self._texture, unit = 2)
				model.texture(self._depth_texture, unit = 3)
		
	def remove(self):
		''' Removes shader '''
		self._shader.remove()
		for model in self._affected_nodes:
			model.unapply(self._shader)
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')
	
	projector = TextureProjector(viz.addTexture('front.png'))
	projector.setPosition(viz.MainView.getPosition())
	projector.affect(piazza)
	
	def update():
		global projector
		projector.update()
		
	vizact.onupdate(0, update)