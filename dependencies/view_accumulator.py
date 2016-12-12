import viz
import vizact

from view_projector import *

class ViewAccumulator(viz.VizNode):
	''' Captures view intensities compiled by a ViewProjector.
	Computed output can be retrieved by getOutputTexture(). 
	Transformation of this node is linked to the transformation of the capture node.
	frame_weight specifies a scaling factor for the accumulation of view intensities.'''
	
	def __init__(self, frame_weight = 0.5, aperture_scale = 0.5, node = None, **kwargs):
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# Create two render textures which we will swap between when updating
		self._output_texture = viz.addRenderTexture()
		self._last_frame_texture = viz.addRenderTexture()
		
		### INIT CAMERA
		# Create render node for camera
		self._cam = viz.addRenderNode(size=(1024, 1024))
		self._cam.renderOnlyToWindows([viz.MainWindow])
		self._cam.setInheritView(False)
		self._cam.drawOrder(1000)
		self._cam.setFov(90.0, 1.0, 0.1,1000.0)
		# Only render once per frame, in case stereo is enabled
		self._cam.setRenderLimit(viz.RENDER_LIMIT_FRAME)
		# set the starting render textures for output and input
		self._cam.setRenderTexture(self._output_texture)
		self._cam.texture(self._last_frame_texture, unit=4)
		# link camera to capture
		viz.link(self._node, self._cam)
		
		# affect camera so its render texture will be computed using the defined shading pipeline
		self._projector = ViewProjector()
		self._projector.setFrameWeight(frame_weight)
		self._projector.setApertureScale(aperture_scale)
		self._projector.affect(self._cam)

		self._update_event = vizact.onupdate(100, self.update)
		
	def update(self):
		# swap textures
		temp = self._output_texture
		self._output_texture = self._last_frame_texture
		self._last_frame_texture = temp
		
		# apply textures
		self._cam.setRenderTexture(self._output_texture)
		self._cam.texture(self._last_frame_texture, unit=4)

		# update transforms for projector
		mat = viz.MainView.getMatrix()
		proj = viz.Matrix.perspective(60.0,1.0,0.1,100.0)
		self._projector.update(self.getMatrix(), mat, proj)

	def setFrameWeight(self, weight):
		''' set scaling factor for per frame view accumulation.
		Float value will be clamped to range [0.0,1.0].'''
		self._projector.setFrameWeight(weight)
		
	def getFrameWeight(self):
		''' get scaling factor for per frame view accumulation.
		Float value returned is in range [0.0,1.0].'''
		return self._projector.getFrameWeight()
		
	def setApertureScale(self, ap_scale):
		''' sets the aperture_scale (scaling factor for the view cone aperture).
		value has to be float in range [0.0,1.0]. '''
		self._projector.setApertureScale(ap_scale)
	
	def getApertureScale(self):
		''' gets the aperture_scale (scaling factor for the view cone aperture).
		value is float in range [0.0,1.0]. '''
		return self._projector.getApertureScale(ap_scale)
		
	def getOutputTexture(self):
		return self._output_texture
	
	def remove(self):
		self._cam.remove()
		self._projector.remove()
		viz.VizNode.remove(self)

if __name__ == '__main__':
	import vizshape
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')
	
	capture = ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5)
	capture.setPosition(0,1.8,3.0)
	
	# add debug quad
	output_quad = vizshape.addQuad()
	output_quad.texture(capture.getOutputTexture())
	output_quad.disable(viz.LIGHTING)
	output_quad.renderOnlyToWindows([viz.addWindow(pos=[0.5, 0.5], size=[0.5, 0.5])])
	viz.link(capture, output_quad)