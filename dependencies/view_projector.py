import viz
import os
import vizmat
import math

def toGL(mat):
	pos = mat.getPosition()
	mat.setPosition(pos[0], pos[1], -pos[2])
	q = mat.getQuat()
	mat.setQuat(-q[0], -q[1], q[2], q[3])
	return mat
	
def clamp(value, min_v, max_v):
	return max(min(value, max_v), min_v)
	
class ViewProjector(object):
	''' Implements a shader effect used to accumulate view intensities. '''
	
	def __init__(self):
		# open the fragment shader, assuming it's relative to this code file
		vertCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'view_projector.vert'), 'r') as vertFile:
			vertCode = vertFile.read()
		fragCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'view_projector.frag'), 'r') as fragFile:
			fragCode = fragFile.read()

		# Make a new shader, and assign some default values for the uniforms.
		# Thesewill be replaced on update.
		self._shader = viz.addShader(frag=fragCode, vert=vertCode)
		
		# temp mat to default set the uniforms
		mat = vizmat.Transform()
		
		# Holds the inverse transform of the main view.
		# This will help to calculate the model matrix inside the shader.
		# Such that vertices can be re-projected into view space of the projector.
		self._inv_view_uni = viz.addUniformMatrix('mainViewMat_inv', mat.get())
		
		# View matrix of the projector.
		self._view_uni = viz.addUniformMatrix('viewMat', mat.get())

		# Projection matrix of the projector.
		self._proj_uni = viz.addUniformMatrix('projMat', mat.get())
		
		# Holds the depth texture to perform inverse shadow mapping.
		# This will allow for projecting only onto first fragment hit.
		self._depth_texture_uni = viz.addUniformInt('depth_tex', 3)
		
		# This allows for accumulation of the previous frames projection
		# along with the actual frames projection.
		self._prev_texture_uni = viz.addUniformInt('prev_frame_tex', 4)
		
		# specifies an additional scaling factor for frame based accumulation (value range [0.1,1.0])
		self._frame_weight_uni = viz.addUniformFloat('frame_weight', 1.0)
		
		# specifies a scaling factor for the view cone aperture (value range [0.0,1.0])
		self._aperture_scale_uni = viz.addUniformFloat('aperture_scale', 1.0)
		
		# attach all uniforms
		self._shader.attach([
			self._inv_view_uni,
			self._view_uni, 
			self._proj_uni, 
			self._depth_texture_uni, 
			self._prev_texture_uni,
			self._frame_weight_uni,
			self._aperture_scale_uni
		])
		
		# Camera used to capture the depth texture.
		self._depth_cam = viz.addRenderNode(inheritView=False)
		self._depth_cam.drawOrder(1000)
		self._depth_cam.setAutoClip(False)
		self._depth_cam.setRenderTexture(viz.addRenderTexture(format=viz.TEX_DEPTH), buffer=viz.RENDER_DEPTH)
		
	def _getDepthTexture(self):
		return self._depth_cam.getRenderTexture(viz.RENDER_DEPTH)
	
	def setFrameWeight(self, weight):
		''' sets the frame_weight (scaling factor for frame based accumulation).
		value has to be float in range [0.0,1.0]. '''
		self._frame_weight_uni.set(clamp(weight, 0.0, 1.0))
	
	def getFrameWeight(self):
		''' gets the frame_weight (scaling factor for frame based accumulation).
		value is float in range [0.0,1.0]. '''
		return self._frame_weight_uni.get()
		
	def setApertureScale(self, ap_scale):
		''' sets the aperture_scale (scaling factor for the view cone aperture).
		value has to be float in range [0.0,1.0]. '''
		self._aperture_scale_uni.set(clamp(ap_scale, 0.0, 1.0))
	
	def getApertureScale(self):
		''' gets the aperture_scale (scaling factor for the view cone aperture).
		value is float in range [0.0,1.0]. '''
		return self._aperture_scale_uni.get()

	def affect(self, model):
		"""Allows a model (VizNode) to be specified as a target for texture projection.

		@model the VizNode object to texture.
		"""
		self._model = model
		self._model.apply(self._shader)
		self._model.texture(self._getDepthTexture(), unit=3)

	def update(self, main_view_mat, view_mat, proj, clusterMask=viz.ALLCLIENTS):
		"""
		@args vizmat.Transform(), vizmat.Transform(), vizmat.Transform(), int
		"""
		# set matrix of depth camera to match this frames projector matrix
		self._depth_cam.setMatrix(view_mat)
		self._depth_cam.setProjectionMatrix(proj)
		# update uniform matrices
		self._inv_view_uni.set(toGL(main_view_mat).get())
		self._view_uni.set(toGL(view_mat).inverse().get())
		self._proj_uni.set(proj.get())

	def remove(self):
		self._shader.remove()