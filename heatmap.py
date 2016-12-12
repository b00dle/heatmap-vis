from dependencies.animation_path_loader import *
from dependencies.animation_path_recorder import *
from dependencies.animation_path_player import *
#from dependencies.omnistereo_frame_recorder import *
from dependencies.view_accumulator_cube import *
from dependencies.heatmap_visualizer import *

_capture_done = False

def recordViewAnimation():
	### replace with your own application setup
	import viz
	import vizcam
	import vizact

	viz.setMultiSample(4)

	viz.go()

	vizcam.WalkNavigate()

	piazza = viz.addChild("piazza.osgb")
	###

	### Add this at the bottom
	'''
	 Create an AnimationPathRecorder and link it to any node, which needs to have it's transformation documented.
	 If 'start' is set to True the recording will start automatically, otherwise you need to start manually.
	 you can specify the file name under which the animation will be saved. '.txt' is automatically added.
	'''
	rec = AnimationPathRecorder(start = False)
	viz.link(viz.MainView, rec)

	# toggle path recording and saving finished recording to a file named 'test_animation.txt'
	def toggleRecord(rec):
		if rec.isRunning():
			rec.stop()
			rec.writeToFile("test_animation")
			print "Animation path saved to test_animation.txt"
		else:
			rec.start()
			print "Animation path recording started."

	vizact.onkeydown('r', toggleRecord, rec)
	###

def captureViewIntensity():
	### replace with your own application setup
	import viz
	import vizact
	import vizcam

	viz.setMultiSample(4)

	viz.go()

	piazza = viz.addChild("piazza.osgb")

	### Add this at the bottom
	'''
	 - Load an animation file, which encapsulates the view rotation for a given time span.
	 - Samples per second determines how many samples are taken along the animation path over the duration of loaded animation.
	 - While the loaded animation path is playing the accumulator will accumulate view intensity values.
	 - After the animation player finished playing these intensities will be saved to a cubemap
	 - The intensity images is then used for final heatmap computation
	'''

	# load animation path
	loader = AnimationPathLoader("test_animation.txt")
	player = AnimationPathPlayer(path = loader.getAnimationPath())
	path_link = viz.link(loader.getAnimationPath(), viz.MainView)
	
	global accumulator
	accumulator = ViewAccumulatorCube(frame_weight = 0.5, aperture_scale = 0.5)
	accumulator.setPosition(viz.MainView.getPosition())

	global _capture_done
	_capture_done = False
	
	cube_textures = {
		viz.POSITIVE_X : accumulator.getOutputTexture(viz.POSITIVE_X),
		viz.NEGATIVE_X : accumulator.getOutputTexture(viz.NEGATIVE_X),
		viz.POSITIVE_Y : accumulator.getOutputTexture(viz.POSITIVE_Y),
		viz.NEGATIVE_Y : accumulator.getOutputTexture(viz.NEGATIVE_Y),
		viz.POSITIVE_Z : accumulator.getOutputTexture(viz.POSITIVE_Z),
		viz.NEGATIVE_Z : accumulator.getOutputTexture(viz.NEGATIVE_Z)
	}
	
	heat_projector = HeatmapVisualizer(cube_textures, auto_update = True)
	heat_projector.setPosition(viz.MainView.getPosition())
	heat_projector.affect(piazza)
	
	# update function capturing accumulating view intensity
	def updateFct(player, accumulator):
		global _capture_done
		
		if not player.isPlaying():
			if not _capture_done:
				accumulator.saveAll()
				_capture_done = True
				print "Intensity capture done."
			elif accumulator != None:
				accumulator.remove()
				accumulator = None
				path_link.remove()

	update = vizact.onupdate(1, updateFct, player, accumulator)
	
def displayHeatmap(project = True):
	'''
	 - Load accumulated view textures
	 - Add cube projector with given textures and shader converting intensities to heat map colors
	 - Let projector affect scene
	 - auto_update = True will set the shader uniforms automatically each frame
	'''
	import viz
	import vizact
	import vizcam

	viz.setMultiSample(4)

	viz.go()

	#vizcam.WalkNavigate()
	
	if project:
		piazza = viz.addChild('piazza.osgb')

		cube_textures = {
			viz.POSITIVE_X : viz.addTexture('accumulated_p_x.bmp'),
			viz.NEGATIVE_X : viz.addTexture('accumulated_n_x.bmp'),
			viz.POSITIVE_Y : viz.addTexture('accumulated_p_y.bmp'),
			viz.NEGATIVE_Y : viz.addTexture('accumulated_n_y.bmp'),
			viz.POSITIVE_Z : viz.addTexture('accumulated_p_z.bmp'),
			viz.NEGATIVE_Z : viz.addTexture('accumulated_n_z.bmp')
		}
		
		heat_projector = HeatmapVisualizer(cube_textures, auto_update = True)
		heat_projector.setPosition(viz.MainView.getPosition())
		heat_projector.affect(piazza)
		
		## GUI for manipulation of the output heatmap
		
		i_slider = viz.addSlider()
		i_x = 1.0 - i_slider.getBoundingBox().width/2.0
		i_y = 0.0 + i_slider.getBoundingBox().height/2.0 
		i_slider.setPosition([i_x, i_y, 0])
		i_slider.set(0.5)

		i_text = viz.addText('intensity scale', parent = viz.SCREEN)
		i_text.setPosition([
			i_x-i_text.getBoundingBox().width/2-i_slider.getBoundingBox().width/2,
			0.01,
			0.0
		])
		i_text.setScale([0.4, 0.4, 1.0])
				
		def onSlider(obj,pos):
			if obj == i_slider:
				heat_projector.setIntensityScale(pos+0.5)
				
		viz.callback(viz.SLIDER_EVENT, onSlider)
	else:
		import vizshape

		env = viz.addEnvironmentMap('accumulated.bmp', faces = ['_p_x', '_n_x', '_p_y', '_n_y', '_p_z', '_n_z'])

		sb = vizshape.addSkyBox()
		sb.texture(env)