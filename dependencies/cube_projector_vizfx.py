import viz
import vizfx

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

class CubeProjectorVizfx(viz.VizNode):
	''' class providing projective texture effect for each side of a cube.
	Projected from similar center.
	Uses vizfx shader specification.
	Constructor takes map of textures of form:
	{
		viz.POSITIVE_X : viz.<Texture>,
		viz.NEGATIVE_X : viz.<Texture>,
		viz.POSITIVE_Y : viz.<Texture>,
		viz.NEGATIVE_Y : viz.<Texture>,
		viz.POSITIVE_Z : viz.<Texture>,
		viz.NEGATIVE_Z : viz.<Texture>
	}'''

	def __init__(self, textures, depth_textures = None, shader_code = None, node = None, **kwargs):

		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()

		viz.VizNode.__init__(self, id = self._node.id, **kwargs)

		# save projective textures
		self._textures = textures

		## Initialize depth cameras.
		# They are used to capture a depth buffer for each face.
		# Inverse shadow mapping is performed based on these buffers,
		# such that the projection only hits the fisrt surface along the projection direction.
		self._depth_cams = {
			viz.POSITIVE_X : viz.addRenderNode(inheritView = False),
			viz.NEGATIVE_X : viz.addRenderNode(inheritView = False),
			viz.POSITIVE_Y : viz.addRenderNode(inheritView = False),
			viz.NEGATIVE_Y : viz.addRenderNode(inheritView = False),
			viz.POSITIVE_Z : viz.addRenderNode(inheritView = False),
			viz.NEGATIVE_Z : viz.addRenderNode(inheritView = False)
		}
		
		# save projective depth textures
		self._depth_textures = {
			viz.POSITIVE_X : None,
			viz.NEGATIVE_X : None,
			viz.POSITIVE_Y : None,
			viz.NEGATIVE_Y : None,
			viz.POSITIVE_Z : None,
			viz.NEGATIVE_Z : None
		}
		
		cube_euler = {
			viz.POSITIVE_X : [90,0,0],
			viz.NEGATIVE_X : [-90,0,0],
			viz.POSITIVE_Y : [0,-90,0],
			viz.NEGATIVE_Y : [0,90,0],
			viz.POSITIVE_Z : [0,0,0],
			viz.NEGATIVE_Z : [-180,0,0]
		}
		
		proj_mat = viz.Matrix.perspective(90.0,1.0,0.1,100.0)

		for cam in self._depth_cams:
			self._depth_cams[cam].drawOrder(1000)
			self._depth_cams[cam].setRenderTexture(
				viz.addRenderTexture(format = viz.TEX_DEPTH),
				buffer = viz.RENDER_DEPTH
			)
			self._depth_cams[cam].setPosition(self.getPosition())
			self._depth_cams[cam].setEuler(cube_euler[cam])
			self._depth_cams[cam].setProjectionMatrix(proj_mat)
			self._depth_cams[cam].setAutoClip(viz.OFF)
			viz.grab(self, self._depth_cams[cam])
			self._depth_textures[cam] = self._depth_cams[cam].getRenderTexture(viz.RENDER_DEPTH)

		# load effect
		code = shader_code
		if code == None:
			code = self._getDefaultShaderCode()
		self._effect = viz.addEffect(code)
		
		# set initial property values
		self._effect.setProperty("Tex_ProjMat", proj_mat)
		self._effect.setProperty("Inv_ViewMat", toGL(viz.MainView.getMatrix().inverse()))
		self._effect.setProperty("Tex_ViewMat_px", toGL(eulerMat(90,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_nx", toGL(eulerMat(-90,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_py", toGL(eulerMat(0,-90,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_ny", toGL(eulerMat(0,90,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_pz", toGL(eulerMat(0,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_nz", toGL(eulerMat(180,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_px", self._textures[viz.POSITIVE_X])
		self._effect.setProperty("Tex_nx", self._textures[viz.NEGATIVE_X])
		self._effect.setProperty("Tex_py", self._textures[viz.POSITIVE_Y])
		self._effect.setProperty("Tex_ny", self._textures[viz.NEGATIVE_Y])
		self._effect.setProperty("Tex_pz", self._textures[viz.POSITIVE_Z])
		self._effect.setProperty("Tex_nz", self._textures[viz.NEGATIVE_Z])
		self._effect.setProperty("TexDepth_px", self._depth_textures[viz.POSITIVE_X])
		self._effect.setProperty("TexDepth_nx", self._depth_textures[viz.NEGATIVE_X])
		self._effect.setProperty("TexDepth_py", self._depth_textures[viz.POSITIVE_Y])
		self._effect.setProperty("TexDepth_ny", self._depth_textures[viz.NEGATIVE_Y])
		self._effect.setProperty("TexDepth_pz", self._depth_textures[viz.POSITIVE_Z])
		self._effect.setProperty("TexDepth_nz", self._depth_textures[viz.NEGATIVE_Z])

	def _getDefaultShaderCode(self):
		''' returns the default vizfx shader specification '''
		return """
			Effect {
				Type "Depth Texture Test"

				Texture2D Tex_px {
					unit 1
				}

				Texture2D Tex_nx {
					unit 2
				}

				Texture2D Tex_py {
					unit 3
				}

				Texture2D Tex_ny {
					unit 4
				}

				Texture2D Tex_pz {
					unit 5
				}

				Texture2D Tex_nz {
					unit 6
				}

				Texture2D TexDepth_px {
					unit 7
				}

				Texture2D TexDepth_nx {
					unit 8
				}

				Texture2D TexDepth_py {
					unit 10
				}

				Texture2D TexDepth_ny {
					unit 11
				}

				Texture2D TexDepth_pz {
					unit 12
				}

				Texture2D TexDepth_nz {
					unit 13
				}

				Matrix4 Tex_ViewMat_px {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ViewMat_nx {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ViewMat_py {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ViewMat_ny {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ViewMat_pz {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ViewMat_nz {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Tex_ProjMat {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Matrix4 Inv_ViewMat {
					value 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 1.0
				}

				Shader {
					BEGIN VertexHeader
						varying vec4 proj_pos_px;
						varying vec4 proj_pos_nx;
						varying vec4 proj_pos_py;
						varying vec4 proj_pos_ny;
						varying vec4 proj_pos_pz;
						varying vec4 proj_pos_nz;
					END

					BEGIN PreTransform
						proj_pos_px = Tex_ProjMat * Tex_ViewMat_px * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
						proj_pos_nx = Tex_ProjMat * Tex_ViewMat_nx * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
						proj_pos_py = Tex_ProjMat * Tex_ViewMat_py * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
						proj_pos_ny = Tex_ProjMat * Tex_ViewMat_ny * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
						proj_pos_pz = Tex_ProjMat * Tex_ViewMat_pz * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
						proj_pos_nz = Tex_ProjMat * Tex_ViewMat_nz * Inv_ViewMat * gl_ModelViewMatrix * gl_Vertex;
					END

					BEGIN FragmentHeader
						varying vec4 proj_pos_px;
						varying vec4 proj_pos_nx;
						varying vec4 proj_pos_py;
						varying vec4 proj_pos_ny;
						varying vec4 proj_pos_pz;
						varying vec4 proj_pos_nz;
					END

					BEGIN FinalColor
						float epsilon = 0.00001;
						vec4 clr = gl_FragColor;

						if(proj_pos_px.z >= 0) {
							proj_pos_px /= proj_pos_px.w;
							float u =  proj_pos_px.x * 0.5 + 0.5f;
							float v =  proj_pos_px.y * 0.5 + 0.5f;
							float z =  proj_pos_px.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_px, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_px, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						if(proj_pos_nx.z >= 0) {
							proj_pos_nx /= proj_pos_nx.w;
							float u =  proj_pos_nx.x * 0.5 + 0.5f;
							float v =  proj_pos_nx.y * 0.5 + 0.5f;
							float z =  proj_pos_nx.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_nx, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_nx, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						if(proj_pos_py.z >= 0) {
							proj_pos_py /= proj_pos_py.w;
							float u =  proj_pos_py.x * 0.5 + 0.5f;
							float v =  proj_pos_py.y * 0.5 + 0.5f;
							float z =  proj_pos_py.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_py, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_py, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						if(proj_pos_ny.z >= 0) {
							proj_pos_ny /= proj_pos_ny.w;
							float u =  proj_pos_ny.x * 0.5 + 0.5f;
							float v =  proj_pos_ny.y * 0.5 + 0.5f;
							float z =  proj_pos_ny.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_ny, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_ny, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						if(proj_pos_pz.z >= 0) {
							proj_pos_pz /= proj_pos_pz.w;
							float u =  proj_pos_pz.x * 0.5 + 0.5f;
							float v =  proj_pos_pz.y * 0.5 + 0.5f;
							float z =  proj_pos_pz.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_pz, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_pz, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						if(proj_pos_nz.z >= 0) {
							proj_pos_nz /= proj_pos_nz.w;
							float u =  proj_pos_nz.x * 0.5 + 0.5f;
							float v =  proj_pos_nz.y * 0.5 + 0.5f;
							float z =  proj_pos_nz.z * 0.5 + 0.5f;
							if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
								vec4 depth = texture2D(TexDepth_nz, vec2(u,v));
								if(z < depth.r+0.0005) {
									vec4 tex_clr = texture2D(Tex_nz, vec2(u,v));
									if(tex_clr.a > 0.0)
										clr = vec4(tex_clr.xyz, 1.0);
								}
							}
						}

						gl_FragColor = clr;
					END
				}
			}
		"""

	def getEffect(self):
		''' returns the shader effect '''
		return self._effect

	def update(self):
		''' updates properties '''
		self._effect.setProperty("Tex_ViewMat_px", toGL(eulerMat(90,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_nx", toGL(eulerMat(-90,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_py", toGL(eulerMat(0,-90,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_ny", toGL(eulerMat(0,90,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_pz", toGL(eulerMat(0,0,0)*self.getMatrix()))
		self._effect.setProperty("Tex_ViewMat_nz", toGL(eulerMat(180,0,0)*self.getMatrix()))
		self._effect.setProperty("Inv_ViewMat", toGL(viz.MainView.getMatrix().inverse()))

	def affect(self, model):
		''' sets effect for node '''
		model.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
		model.apply(self._effect)

if __name__ == '__main__':
	import vizcam
	import vizact
	import vizshape


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
	
	cube_proj = CubeProjectorVizfx(cube_textures)
	cube_proj.setPosition([0, 1.8, 0])
	cube_proj.affect(piazza)
	
	def update():
		global cube_proj
		cube_proj.update()
	vizact.onupdate(0, update)
