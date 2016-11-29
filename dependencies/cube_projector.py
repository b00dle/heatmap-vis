import viz
import os
import vizshape
import vizact

def toGL(mat = viz.Matrix()):
	''' Converts a vizard matrix to a GL matrix. '''
	temp_mat = viz.Matrix(mat)
	quat = temp_mat.getQuat()
	pos = temp_mat.getPosition()
	temp_mat.setPosition(pos[0], pos[1], -pos[2])
	temp_mat.setQuat(-quat[0], -quat[1], quat[2], quat[3])
	return temp_mat.inverse()
	
def eulerMat(yaw, pitch, roll):
	''' returns a transformation matrix based on given euler angles '''
	m = viz.Matrix()
	m.setEuler(yaw, pitch, roll)
	return m	

class CubeProjector(viz.VizNode):
	''' class providing projective texture effect for each side of a cube. 
	Projected from similar center. 
	Uses plain GLSL shader specification.
	Constructor takes map of textures of form: 
	{
		viz.POSITIVE_X : viz.<Texture>,
		viz.NEGATIVE_X : viz.<Texture>,
		viz.POSITIVE_Y : viz.<Texture>,
		viz.NEGATIVE_Y : viz.<Texture>,
		viz.POSITIVE_Z : viz.<Texture>,
		viz.NEGATIVE_Z : viz.<Texture>
	}'''
	
	def __init__(self, textures, shader = None, node = None, **kwargs):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# save projective textures
		self._textures = textures
		for key in self._textures:
			self._textures[key].wrap(viz.WRAP_S, viz.CLAMP_TO_BORDER)
			self._textures[key].wrap(viz.WRAP_T, viz.CLAMP_TO_BORDER)
		
		# check if shader has been given
		self._shader = shader
		if self._shader == None:
			# open the shaders, assuming it's relative to this code file
			vertCode = ""
			with open(os.path.join(os.path.dirname(__file__), 'cube_project.vert'), 'r') as vertFile:
				vertCode = vertFile.read()
			fragCode = ""
			with open(os.path.join(os.path.dirname(__file__), 'cube_project.frag'), 'r') as fragFile:
				fragCode = fragFile.read()
			# add shader from code
			self._shader = viz.addShader(frag=fragCode, vert=vertCode)
						
		# set projection matrix
		self._projection_mat = viz.Matrix.perspective(90.0,1.0,0.1,100.0)
		
		# add uniforms for shader and initialize with default values
		self._uniform_tex_proj = viz.addUniformMatrix('tex_ProjMat', self._projection_mat.get())

		# texture uniforms
		self._uniform_proj_texture = { 
			viz.POSITIVE_X : viz.addUniformInt('projectionTex_PX', 2),
			viz.NEGATIVE_X : viz.addUniformInt('projectionTex_NX', 3),
			viz.POSITIVE_Y : viz.addUniformInt('projectionTex_PY', 4),
			viz.NEGATIVE_Y : viz.addUniformInt('projectionTex_NY', 5),
			viz.POSITIVE_Z : viz.addUniformInt('projectionTex_PZ', 6),
			viz.NEGATIVE_Z : viz.addUniformInt('projectionTex_NZ', 7)
		}
		
		# uniforms for view matrices of texture projections
		m = self.getMatrix()
		self._uniform_tex_view = {
			viz.POSITIVE_X : viz.addUniformMatrix('tex_ViewMat_PX', toGL(eulerMat(90,0,0)*m).get()),
			viz.NEGATIVE_X : viz.addUniformMatrix('tex_ViewMat_NX', toGL(eulerMat(-90,0,0)*m).get()),
			viz.POSITIVE_Y : viz.addUniformMatrix('tex_ViewMat_PY', toGL(eulerMat(0,-90,0)*m).get()),
			viz.NEGATIVE_Y : viz.addUniformMatrix('tex_ViewMat_NY', toGL(eulerMat(0,90,0)*m).get()),
			viz.POSITIVE_Z : viz.addUniformMatrix('tex_ViewMat_PZ', toGL(eulerMat(0,0,0)*m).get()),
			viz.NEGATIVE_Z : viz.addUniformMatrix('tex_ViewMat_NZ', toGL(eulerMat(180,0,0)*m).get())
		}
		
		# attach uniforms to shader
		uniforms = [self._uniform_tex_proj]
		for face in self._uniform_tex_view:
			uniforms.append(self._uniform_proj_texture[face])
			uniforms.append(self._uniform_tex_view[face])
			
		self._shader.attach(uniforms)
		
		vizact.onupdate(1, self._update)
		
	def _update(self):
		''' Function called on update. Will set uniform values. '''
		# set uniform projection matrix
		self._uniform_tex_proj.set(self._projection_mat.get())
		
		# set uniform view mat transforms
		m = self.getMatrix()
		self._uniform_tex_view[viz.POSITIVE_X].set(toGL(eulerMat(90,0,0)*m).get())
		self._uniform_tex_view[viz.NEGATIVE_X].set(toGL(eulerMat(-90,0,0)*m).get())
		self._uniform_tex_view[viz.POSITIVE_Y].set(toGL(eulerMat(0,-90,0)*m).get())
		self._uniform_tex_view[viz.NEGATIVE_Y].set(toGL(eulerMat(0,90,0)*m).get())
		self._uniform_tex_view[viz.POSITIVE_Z].set(toGL(eulerMat(0,0,0)*m).get())
		self._uniform_tex_view[viz.NEGATIVE_Z].set(toGL(eulerMat(180,0,0)*m).get())
		
	def affect(self, model):
		'''Allows a model (VizNode) to be specified as a target for cube texture projection.

		@model the VizNode object to texture.
		'''
		model.apply(self._shader)
		i = 2
		for face in self._textures:
			model.texture(self._textures[face], unit = i)
			i += 1
			
	def getShader(self):
		''' Returns the shader of this instance '''
		return self._shader
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')

	cube_textures = {
		viz.POSITIVE_X : viz.addTexture('right.png'),
		viz.NEGATIVE_X : viz.addTexture('left.png'),
		viz.POSITIVE_Y : viz.addTexture('up.png'),
		viz.NEGATIVE_Y : viz.addTexture('down.png'),
		viz.POSITIVE_Z : viz.addTexture('front.png'),
		viz.NEGATIVE_Z : viz.addTexture('back.png')
	}
	
	cube_proj = CubeProjector(cube_textures)
	cube_proj.setPosition(viz.MainView.getPosition())
	cube_proj.affect(piazza)