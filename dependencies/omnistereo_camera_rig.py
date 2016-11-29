import math
import viz
import vizcam


import math

import viz
import vizfx
import vizmat

default_shader = """
Effect {
	Texture2D CameraImage {
		unit 0
	}
	
	Int Slices {
		value 1
	}
	
	Float PI {
		value 3.1415926535897932384626433832795
	}
	
	Float uvScale {
		value 1 1
	}
	
	Float uvOffset {
		value 0 0
	}
	
	Float projMat0 {
		value 1 0 0 0
	}
	Float projMat1 {
		value 0 1 0 0
	}
	Float projMat2 {
		value 0 0 1 0
	}
	Float projMat3 {
		value 0 0 0 1
	}
	
	Float xShift {
	}
	
	Matrix4 MVP {
	}
	
	Shader {
		BEGIN FinalColor
		
		float u = uvCameraImage[0];
		float v = uvCameraImage[1];
		
		uvCameraImage *= uvScale;
		uvCameraImage += uvOffset;

		float theta = uvCameraImage[0]*PI*2.0 - xShift;
		float phi = uvCameraImage[1]*PI - PI/2.0;
		
		float x = sin(theta) * cos(phi);
		float y = sin(phi);
		float z = cos(theta) * cos(phi);
		
		mat4 projMat = mat4(projMat0, projMat1, projMat2, projMat3);
		vec4 ruv = vec4( x, y, z, 0) * projMat;
		
		u = 1.0-(ruv[0]/ruv[2]+1.0)*0.5;
		v = 1.0-(ruv[1]/ruv[2]+1.0)*0.5;
		
		gl_FragColor = texture2D(CameraImage, vec2(u, v));
		
		END
	}
}
"""

class OmnistereoCameraRig(viz.VizNode):
	'''creates a 360 degree stereoscopic video capture from it's current position'''
	
	## constructor
	def __init__(self, horizontal_samples = 20, vertical_samples = 1, width = 1080, eye_distance = 0.065, mono = False, node = None, **kwargs):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
		
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# number of slices per eye
		self._horizontal_samples = horizontal_samples
		self._vertical_samples = vertical_samples
		
		# height and width of the panorama (per eye)
		self._output_height = int(width / 2.0)
		self._output_width = width
		
		# physical size of the output texture
		output_aspect = self._output_width / self._output_height
		self._output_physical_size = [1.0*output_aspect, 1.0]
		
		# height of the output panorama
		self._output_height = self._output_height
		
		# eye distance for the stereo setup
		self._eye_distance = eye_distance
		
		# list of tex quads for samples taken to stitch the panorama
		self._eye_output = []
		
		# will only render one eye panorama if True
		self._mono = mono
	
	def init(self, trn=None):
		# initialize camera rig
		self._secondWindow = trn
		if self._mono:
			self._initCameras(0, windowPos=[0, 0])
		else:
			self._initCameras(-self._eye_distance/2.0, windowPos=[0, -self._output_physical_size[1]/2.0])
			self._initCameras(self._eye_distance/2.0, windowPos=[0, self._output_physical_size[1]/2.0])
	
	def getSize(self):
		"""returns the normalized size of the stitched texture"""
		if self._mono:
			return [self._output_physical_size[0], self._output_physical_size[1]]
		else:
			return [self._output_physical_size[0], self._output_physical_size[1]*2.0]
	
	def _computeFrustum(self, vert_angle):
		"""Compute frustum of wall given a head position"""
		h_opening = (3.0*math.pi/float(self._horizontal_samples))
		v_opening = (math.pi/float(self._vertical_samples))
		
		bottom_angle = -vert_angle - (v_opening / 2.0)
		top_angle = -vert_angle + (v_opening / 2.0)
		
		left_angle = -(h_opening/2.0)
		right_angle = (h_opening/2.0)
		top_angle = min(math.pi/2.0, top_angle)
		bottom_angle = max(-math.pi/2.0, bottom_angle)
		
		#Calculate frustum
		near = 0.01
		left = math.tan(left_angle)*near
		right = math.tan(right_angle)*near
		bottom = math.tan(bottom_angle)*near
		top = math.tan(top_angle)*near
		far = 10000.0
		
		#Return frustum values
		return left,right,bottom,top,near,far
	
	def _initCameras(self, x, windowPos):
		hor_angle = (360.0/float(self._horizontal_samples))
		vert_angle = (180.0/float(self._vertical_samples))
		if vert_angle == 180:
			vert_angle = 90
		aspect = math.tan(hor_angle*0.5*math.pi/180.0) / math.tan(vert_angle*0.5*math.pi/180.0)
		height = self._output_height/self._vertical_samples
		width = int((hor_angle/vert_angle)*height)
		
		eye_tex = []
		
		yaw = 360.0 / float(self._horizontal_samples)
		pitch = 180.0 / float(self._vertical_samples)
		output_scale = 1.0/float(self._vertical_samples)
		
		self._effect = viz.addEffect(default_shader)
		
		for i in range(0, self._vertical_samples):
			eye_tex.append([])
			
			vert_angle = 90.0 - (i*pitch) - pitch/2.0
			for j in range(0,self._horizontal_samples):
				cam = viz.addRenderNode(size = (width*4, height*4))
				cam.setInheritView(False)
				cam.setMatrix(viz.Matrix())
				
				mat = viz.Matrix()
				left, right, bottom, top, near,far = self._computeFrustum(0)
				mat.makeFrustum(left, right, bottom, top, near, far)
				
				cam.setProjectionMatrix(mat)
				cam.setEuler(j*yaw, vert_angle, 0.0)
				
				cam.setRenderTexture(viz.addRenderTexture())
				cam.setRenderLimit(viz.RENDER_LIMIT_FRAME)
				pos = vizmat.Vector([x, 0, 0])
				rm = vizmat.Transform()
				rm.setEuler([j*yaw, 0, 0])
				pos = rm.preMultVec(pos)
				link = viz.link(self._node, cam)
				link.setSrcFlag(viz.ABS_GLOBAL)
				link.setDstFlag(viz.ABS_GLOBAL)
				link.setMask(viz.LINK_POS|viz.LINK_ORI)
				link.preTrans(pos)
				link.preEuler([j*yaw, vert_angle, 0.0])
				eye_tex[i].append(cam.getRenderTexture())
		
		self._outputNode = viz.addGroup()
		self._outputNode.setParent(self)
		
		tex_quad_size = [self._output_physical_size[0]/self._horizontal_samples,
						self._output_physical_size[1]/self._vertical_samples]
		startingX = -0.5 * self._output_physical_size[0] + tex_quad_size[0]/2.0 + windowPos[0]
		startingY = -0.5 * self._output_physical_size[1] + tex_quad_size[1]/2.0 + windowPos[1]
		
		for i in range(0, self._vertical_samples):
			vert_angle = 90.0 - (i*pitch) - pitch/2.0
			for j in range(0, self._horizontal_samples):
				stitched_quad = viz.addTexQuad()
				stitched_quad.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
				
				stitched_quad.setParent(self._outputNode)
				stitched_quad.texture(eye_tex[i][j])
				stitched_quad.setSize(tex_quad_size)
				stitched_quad.setPosition(startingX + float(j)*tex_quad_size[0], startingY + float(i)*tex_quad_size[1], 0.0)# + 0.1*i
				
				self._eye_output.append(stitched_quad)
				self._outputNode.apply(self._effect)
				uv_scale = [1.0/self._horizontal_samples, 1.0/self._vertical_samples]
				stitched_quad.setUniformFloat('uvScale', uv_scale)
				stitched_quad.setUniformFloat('uvOffset', [float(j)*uv_scale[0], float(i)*uv_scale[1]])
				
				# set the projection matrix so we can sample correctly
				mv_mat = vizmat.Transform()
				mv_mat.setEuler(j*yaw, vert_angle, 0.0)
				
				left, right, bottom, top, near, far = self._computeFrustum(0)
				mat = viz.Matrix()
				mat.makeFrustum(left, right, bottom, top, near, far)
				mat.preMult(mv_mat.inverse())
				mat.transpose()
				
				stitched_quad.setUniformFloat('projMat0', mat[0:4])
				stitched_quad.setUniformFloat('projMat1', mat[4:8])
				stitched_quad.setUniformFloat('projMat2', mat[8:12])
				stitched_quad.setUniformFloat('projMat3', mat[12:16])
				
				stitched_quad.setUniformFloat('xShift', math.pi/self._horizontal_samples)
				stitched_quad.renderOnlyToRenderNodes([self._secondWindow])
	
	def getWindow(self):
		return self._secondWindow
	
	## returns the cull mask of the camera
	def getCullMask(self):
		return self._mask
		
	def getNumHorizontalSlices(self):
		return self._horizontal_samples
		
	def isMono(self):
		'''returns if this rig captures mono (only one eye)'''
		return self._mono