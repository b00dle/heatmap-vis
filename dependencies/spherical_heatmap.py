import viz
import vizshape
import vizact
import vizfx
import math

from omnistereo_frame_recorder import *
from animation_path_player import *

def _magnitude(v):
		return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))
		
def _normalize(v):
	vmag = _magnitude(v)
	return [ v[i]/vmag  for i in range(len(v)) ]

class _VertexProperties:
	"""Helper class holding vertex properties"""
	
	def __init__(self, view_duration = 0.0):		
		# duration the view spent looking at vertex
		self.view_duration = view_duration

class SphericalHeatmap(viz.VizNode):
	"""Constructs Heatmap Data from given animation path capturing view transformation"""
	
	def __init__(self, path, samples_per_second = 30, sphere_slices = 100, sphere_stacks = 100, node = None, **kwargs):

		# node to reference this instance in the scenegraph
		self._node = node
		if self._node == None:
			self._node = viz.addGroup()
			
		viz.VizNode.__init__(self, id = self._node.id, **kwargs)
		
		# samples along the animation path taken per second for construction of the heatmap
		self._sps = samples_per_second
		
		# vertices sampling color along the heatmap
		# position and count will be equal to initial position of sphere vertices 
		self._vertices = []
		
		# captures maximum view duration for all vertices
		self._max_view_duration = 0.0
		
		# sphere displaying heatmap
		self._sphere = vizshape.addSphere(4.0, sphere_slices, sphere_stacks)
		self._sphere.visible(viz.OFF)
		self._sphere.disable(viz.CULL_FACE)
		self._sphere.disable(viz.LIGHTING)
		self._sphere.disable(viz.SHADOWS)
		self._sphere.disable(viz.SHADOW_CASTING)
		self._sphere.generateEffects(viz.EFFECTGEN_DEFAULT, vizfx.getComposer())
		self._sphere.apply(viz.addEffect(self._shaderCode()))
		self._sphere.dynamic()
		
		# <animationpath> for construction of the heatmap
		self._path = path
		self._path_player = AnimationPathPlayer(frame_rate = self._sps, path = self._path, start = False)
				
		# update function for heatmap construction
		self._updateFct = vizact.onupdate(1, self._update)
		self._updateFct.setEnabled(False)
		
		# link to the output node, switched off when capturing
		self._output_link = viz.link(self._node, self._sphere)
		self._output_link.setEnabled(False)
		
		self._initVertices()
	
	def isConstructing(self):
		"""returns True if the heatmap is currently being constructed.
		False otherwise."""
		return self._updateFct.getEnabled()
	
	def _update(self):
		"""function called each frame"""
		if not self._path_player.isPlaying():
			self._colorizeHeatmap()
			self._output_link.setEnabled(True)
			self._sphere.visible(viz.ON)
			self._updateFct.setEnabled(False)
			print "max duration:", self._max_view_duration
			return
	
		progress = (self._path.getTime() / self._path.getDuration()) * 100.0
		print "progress constructing data: ", progress, "%"
	
		self._sphere.setPosition(self._path.getPosition())
	
		weight = 1.0 / (self._path.getDuration()*self._sps)
		for i in range(0, self._sphere.getVertexCount()):
			vertex_pos = self._sphere.getVertex(i, viz.ABS_GLOBAL)
			view_dir = self._path.getMatrix().getForward()
			view_pos = self._path.getPosition(viz.ABS_GLOBAL)
			
			vertex_dir = _normalize([
				(vertex_pos[0] - view_pos[0]),
				(vertex_pos[1] - view_pos[1]),
				(vertex_pos[2] - view_pos[2])
			])
			
			angle = math.degrees(math.acos(vertex_dir[0]*view_dir[0]+vertex_dir[1]*view_dir[1]+vertex_dir[2]*view_dir[2]))
			if(angle < 15):
				self._vertices[i].view_duration += (1-(angle/15.0)) * weight
				if self._vertices[i].view_duration > self._max_view_duration:
					self._max_view_duration = self._vertices[i].view_duration
	
	def _shaderCode(self):
		"""Returns code for shader effect used to visualize output heatmap"""
		return """
			Effect {
				Shader {
					BEGIN FinalColor

					gl_FragColor = vizfx_VertexColor;
					
					END
				}
			}
		"""
	
	def _colorizeHeatmap(self):
		"""colorizes vertices of sphere based on captured data"""
		print "===================================================\nStarting sphere colorizing"
		for i in range(0, self._sphere.getVertexCount()):
			intensity = self._vertices[i].view_duration / self._max_view_duration
			r = 0.0
			g = 0.0
			b = 0.0
			a = 0.5
			if intensity > 0.7:
				r = (intensity - 0.3)/0.7
				g = 1.0-r
			elif intensity > 0.4:
				g = (intensity - 0.3)/0.4
				b = 1.0-g
			elif intensity > 0.1:
				b = (intensity - 0.3)/0.1
				a *= (intensity - 0.3)/0.1
			else:
				a = 0.0
			self._sphere.setVertexColor(i,r,g,b,a)
		print "===================================================\nDONE."
	
	def _initVertices(self):
		"""Initializes vertices on sphere map"""
		self._vertices = []
		for i in range(0, self._sphere.getVertexCount()):
			self._vertices.append(_VertexProperties())
			
	def construct(self):
		"""initiates the capture process, by triggering playback of
		<animationpath> given upon init."""
		self._path.setTime(0.0)
		self._max_view_duration = 0.0
		for vert in self._vertices:
			vert.view_duration = 0.0
		self._path_player.play()
		self._sphere.visible(viz.OFF)
		self._output_link.setEnabled(False)
		self._updateFct.setEnabled(True)
		print "===================================================\nStarting data construction"
		
if __name__ == '__main__':
	import vizcam
	from animation_path_loader import *
		
	viz.setMultiSample(4)
	
	viz.go()
	
	piazza = viz.addChild("piazza.osgb")
	
	vizcam.WalkNavigate()
	
	loader = AnimationPathLoader("test_animation.txt")
	
	heat_map = SphericalHeatmap(loader.getAnimationPath(), samples_per_second = 10, sphere_slices = 100, sphere_stacks = 100)
	heat_map.setPosition(0,1.8,0.0)
	heat_map.construct()

	capture_done = False
	
	def await_capture(hm):
		global capture_done
		if not hm.isConstructing() and not capture_done:
			omni_rec = OmnistereoFrameRecorder(
				pixel_width = 4096,
				out_name = "test_heat",
				mono = True
			)
			capture_done = True
		
	update = vizact.onupdate(1, await_capture, heat_map)