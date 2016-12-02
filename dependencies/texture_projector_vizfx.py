import viz
import os
import vizshape
import vizact
import vizfx

def toGL(mat = viz.Matrix()):
	""" Converts a vizard matrix to a GL matrix. """
	temp_mat = viz.Matrix(mat)
	quat = temp_mat.getQuat()
	pos = temp_mat.getPosition()
	temp_mat.setPosition(pos[0], pos[1], -pos[2])
	temp_mat.setQuat(-quat[0], -quat[1], quat[2], quat[3])
	return temp_mat.inverse()

class TextureProjectorVizfx(viz.VizNode):
	''' class providing projective texture effect '''
	
	instance_count = 0
	
	def __init__(
		self,
		texture,
		projection_matrix = viz.Matrix.perspective(90.0,1.0,0.1,100.0),
		view_node = viz.MainView,
		shader_code = None,
		node = None,
		**kwargs
		):
		
		TextureProjectorVizfx.instance_count += 1		
		
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
		#self._depth_cam.setAutoClip(viz.OFF)
		viz.link(self, self._depth_cam)
		
		# Depth cam for observer
		self._observer_depth_cam = viz.addRenderNode(inheritView = False)
		self._observer_depth_cam.drawOrder(100)
		self._observer_depth_cam.setRenderTexture(
			viz.addRenderTexture(format = viz.TEX_DEPTH),
			buffer = viz.RENDER_DEPTH
		)
		self._observer_depth_cam.setProjectionMatrix(self._projection_mat)
		#self._observer_depth_cam.setAutoClip(viz.OFF)
		viz.link(viz.MainView, self._observer_depth_cam)
		
		# depth texture captured by camera
		self._depth_texture = self._depth_cam.getRenderTexture(viz.RENDER_DEPTH)
		
		# depth texture captured by observer camera
		self._observer_depth_texture = self._observer_depth_cam.getRenderTexture(viz.RENDER_DEPTH)
		
		# load effect
		code = shader_code
		if code == None:
			code = self._getDefaultShaderCode()
		self._effect = viz.addEffect(code)
		
		self._effect.setProperty("Tex_ProjMat", self._projection_mat)
		self._effect.setProperty("Inv_ViewMat", toGL(self._view_node.getMatrix(viz.ABS_GLOBAL).inverse()))
		self._effect.setProperty("Tex_ViewMat", toGL(self.getMatrix(viz.ABS_GLOBAL)))
		self._effect.setProperty("Tex", self._texture)
		self._effect.setProperty("TexDepth", self._depth_texture)
		self._effect.setProperty("ObserverDepth", self._observer_depth_texture)
		self._effect.setProperty("Observer_ViewMat", toGL(viz.MainView.getMatrix(viz.ABS_GLOBAL)))
		
	def update(self):
		''' Function called on update. Will set uniform values. '''
		self._effect.setProperty("Inv_ViewMat", toGL(self._view_node.getMatrix(viz.ABS_GLOBAL).inverse()))
		self._effect.setProperty("Tex_ViewMat", toGL(self.getMatrix(viz.ABS_GLOBAL)))
		self._effect.setProperty("Observer_ViewMat", toGL(viz.MainView.getMatrix(viz.ABS_GLOBAL)))
	
	def affect(self, model):
		"""Allows a model (VizNode) to be specified as a target for texture projection.

		@model the VizNode object to texture.
		"""
		model.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
		model.apply(self._effect)
		
	def remove(self):
		''' Removes shader '''
		pass
	
	def _getDefaultShaderCode(self):
		''' returns the default vizfx shader specification '''
		return """ 
		Effect {
			Type "Projective Texture """+str(TextureProjectorVizfx.instance_count)+""""
			
			Texture2D Tex {
				unit 10
			}
			
			Texture2D TexDepth {
				unit 11
			}

			Texture2D ObserverDepth {
				unit 12
			}

			Matrix4 Tex_ViewMat {
				value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
			}

			Matrix4 Tex_ProjMat {
				value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
			}

			Matrix4 Inv_ViewMat {
				value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
			}
			
			Matrix4 Observer_ViewMat {
				value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
			}

			Shader {
				BEGIN VertexHeader
					varying vec4 proj_pos;
					varying vec4 observer_pos;
				END

				BEGIN PreTransform
					proj_pos = Tex_ProjMat * /*Tex_ViewMat * Inv_ViewMat */ gl_ModelViewMatrix * gl_Vertex;
					observer_pos = Tex_ProjMat * Observer_ViewMat * inverse(Tex_ViewMat) * gl_ModelViewMatrix * gl_Vertex;
				END

				BEGIN FragmentHeader
					varying vec4 proj_pos;
					
					varying vec4 observer_pos;
				END

				BEGIN FinalColor
					float epsilon = 0.00001;
					vec4 clr = vec4(0.0,0.0,0.0,1.0); //gl_FragColor;//vec4(0,0,0,1);

					/////////////////////////////////////////////
					///////// GET COLOR FROM PROJECTION /////////
					/////////////////////////////////////////////
					
					if(proj_pos.z >= 0.0) {
						vec4 div_coord = proj_pos / proj_pos.w;
						float u =  div_coord.x * 0.5 + 0.5;
						float v =  div_coord.y * 0.5 + 0.5;
						float z =  div_coord.z * 0.5 + 0.5;
						if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
							vec4 depth = texture2D(TexDepth, vec2(u,v));
							if(z < depth.r+0.0005) {
								vec4 tex_clr = texture2D(Tex, vec2(u,v));
								if(tex_clr.a > 0.0)
									clr += tex_clr;
							}
						}
					}
					
					/////////////////////////////////////////////
					//////////// GET OBSERVED COLOR /////////////
					/////////////////////////////////////////////
					
					if(observer_pos.z >= 0.0) {
						vec4 div_coord = observer_pos / observer_pos.w;
						float u =  div_coord.x * 0.5 + 0.5;
						float v =  div_coord.y * 0.5 + 0.5;
						float z =  div_coord.z * 0.5 + 0.5;
						float offset = 0.05;
						if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
							float dist = length(div_coord.xy);
							vec4 depth = texture2D(ObserverDepth, vec2(u,v));
							if(z < depth.r+0.0005 && dist < offset) {
								float i = 1-(dist/offset);
								i = max(0.01, i);
								clr += vec4(i,i,i,1.0);
							}
						}
					}
					
					
					gl_FragColor = vec4(clr.r,clr.g,clr.b,1.0);
				END
			}
		}
	"""
		
if __name__ == '__main__':
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')

	ren_node = viz.addRenderNode(inheritView = False)
	ren_node.setProjectionMatrix(viz.Matrix.perspective(90.0,1.0,0.1,100.0))
	ren_node.setRenderTexture(viz.addRenderTexture(size = [512,512]))
	ren_node.setPosition(viz.MainView.getPosition())
	ren_node.setClearMask(viz.GL_DEPTH_BUFFER_BIT)
	
	projector = TextureProjectorVizfx(ren_node.getRenderTexture(), view_node = ren_node)
	projector.setPosition(viz.MainView.getPosition())
	projector.affect(piazza)
	
	def update():
		global projector
		projector.update()
		
	vizact.onupdate(0, update)
	
	# use ren_node.getRenderTexture().save(<name>) to see the correct caption
	# vizfx shader matrices are set accoring to the render node