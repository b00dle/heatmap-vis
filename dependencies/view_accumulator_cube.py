import viz

from view_accumulator import *

class ViewAccumulatorCube(viz.VizNode):
	''' Captures view intensities using a cube setup.
	Each face is represented by a ViewAccumulator.
	Computed output can be retrieved by getOutputTexture(face).
	All textures can be stored calling saveAll(...).
	Transformation of this node is linked to transformation of the center of the cube. '''
	
	def __init__(self, frame_weight = 0.5, aperture_scale = 0.5, node = None, **kwargs):
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# init intensity capture for each face
		self._capture_faces = {
			viz.POSITIVE_X : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5),
			viz.NEGATIVE_X : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5),
			viz.POSITIVE_Y : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5),
			viz.NEGATIVE_Y : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5),
			viz.POSITIVE_Z : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5),
			viz.NEGATIVE_Z : ViewAccumulator(frame_weight = 0.5, aperture_scale = 0.5)
		}
		
		cube_euler = {
			viz.POSITIVE_X : [90,0,0],
			viz.NEGATIVE_X : [-90,0,0],
			viz.POSITIVE_Y : [0,-90,0],
			viz.NEGATIVE_Y : [0,90,0],
			viz.POSITIVE_Z : [0,0,0],
			viz.NEGATIVE_Z : [-180,0,0]
		}
		
		# transform face captures according to face orientation
		for face in self._capture_faces:
			self._capture_faces[face].setEuler(cube_euler[face])
			viz.grab(self,self._capture_faces[face])
			
	def getOutputTexture(self, face = viz.POSITIVE_Z):
		return self._capture_faces[face].getOutputTexture()
		
	def setFrameWeight(self, weight):
		''' set scaling factor for per frame view accumulation.
		Float value will be clamped to range [0.0,1.0].'''
		for face in self._capture_faces:
			self._capture_faces[face].setFrameWeight(weight)
		
	def getFrameWeight(self, face = viz.POSITIVE_Z):
		''' get scaling factor for per frame view accumulation.
		Float value returned is in range [0.0,1.0].'''
		return self._capture_faces[face].getFrameWeight()
		
	def setApertureScale(self, ap_scale):
		''' sets the aperture_scale (scaling factor for the view cone aperture).
		value has to be float in range [0.0,1.0]. '''
		for face in self._capture_faces:
			self._capture_faces[face].setApertureScale(ap_scale)
	
	def getApertureScale(self, face = viz.POSITIVE_Z):
		''' gets the aperture_scale (scaling factor for the view cone aperture).
		value is float in range [0.0,1.0]. '''
		return self._capture_faces[face].getApertureScale(ap_scale)
		
	def saveAll(self, prefix = "accumulated", directory = ""):
		''' saves all cube face captures to .bmp file.
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
		
		for face in self._capture_faces:
			self._capture_faces[face].getOutputTexture().save(paths[face])
	
	def remove(self):
		for face in self._capture_faces:
			self._capture_faces[face].remove()
		viz.VizNode.remove(self)
			
if __name__ == '__main__':
	import vizshape
	import vizcam
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')
	
	cube_capture = ViewAccumulatorCube()
	cube_capture.setPosition(viz.MainView.getPosition())
	
	# call cube_capture.saveAll() after some time of capturing 
	# to view the accumulated view intensities