from observer_projector import *
from cube_map_camera import CubeMapCamera
	
class Accumulator(viz.VizNode):
	
	def __init__(self, shader = None, node = None, **kwargs):
		
		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# setup nodes for faces
		self._cube_cam = CubeMapCamera()
		viz.link(self, self._cube_cam)
		#self._cube_cam.setPosition(viz.MainView.getPosition())
		
		# initialize one projector per face
		self._projectors = {
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
	
		self._cube_cam.setClearMask(viz.GL_DEPTH_BUFFER_BIT)
		for face in self._projectors:
			self._projectors[face] = ObserverProjector( 
				self._cube_cam.getCubeMapCameras()[face].getRenderTexture(),
				observer_node = viz.MainView,
				view_node = self._cube_cam.getCubeMapCameras()[face]
			)
			self._projectors[face].setPosition(self.getPosition())
			self._projectors[face].setEuler(cube_euler[face])
			self._projectors[face].affect(self._cube_cam.getCubeMapCameras()[face])
			viz.grab(self, self._projectors[face])
		
	def update(self):
		''' updates all projectors '''
		for face in self._projectors:
			self._projectors[face].update()
			
	def saveAll(self, prefix = "accumulated", directory = ""):
		''' saves all cube map textures to file. Returns full paths of saved files. '''
		return self._cube_cam.saveAll(prefix, directory)
			
if __name__ == '__main__':
	import vizcam
	import vizact
	
	viz.setMultiSample(4)
	viz.fov(60)
	viz.go()

	vizcam.WalkNavigate()
	
	piazza = viz.addChild('piazza.osgb')
	
	acc = Accumulator()
	acc.setPosition(viz.MainView.getPosition())
	
	def update():
		global acc
		acc.update()
		
	vizact.onupdate(0, update)