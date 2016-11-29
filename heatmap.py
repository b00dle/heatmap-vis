from dependencies.animation_path_loader import *
from dependencies.animation_path_recorder import *
from dependencies.animation_path_player import *
#from dependencies.omnistereo_frame_recorder import *
from dependencies.accumulator import *
from dependencies.cube_projector_vizfx import *

# shader code used to render the heatmap from accumulated view intensities
_heatmap_shader = """
	Effect {
		Type "Projective Texture Cubemap"
		
		Texture2D Tex_px {
			unit 10
		}

		Texture2D Tex_nx {
			unit 12
		}

		Texture2D Tex_py {
			unit 13
		}

		Texture2D Tex_ny {
			unit 14
		}

		Texture2D Tex_pz {
			unit 15
		}

		Texture2D Tex_nz {
			unit 16
		}

		Texture2D TexDepth_px {
			unit 17
		}

		Texture2D TexDepth_nx {
			unit 18
		}

		Texture2D TexDepth_py {
			unit 19
		}

		Texture2D TexDepth_ny {
			unit 20
		}

		Texture2D TexDepth_pz {
			unit 21
		}

		Texture2D TexDepth_nz {
			unit 22
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

				/////////////////////////////////////////////
				///////// GET COLOR FROM PROJECTION /////////
				/////////////////////////////////////////////

				vec4 proj_clr = vec4(0.0);

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
								proj_clr += tex_clr;
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
								proj_clr += tex_clr;
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
								proj_clr += tex_clr;
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
								proj_clr += tex_clr;
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
								proj_clr += tex_clr;
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
								proj_clr += tex_clr;
						}
					}
				}

				/////////////////////////////////////////////
				////// CONVERT INTENSITY TO HEAT COLOR //////
				/////////////////////////////////////////////

				// should be same, but let's interpolate to be sure
				float i = 0.33333 * proj_clr.r + 0.33333 * proj_clr.g + 0.33333 * proj_clr.b;
				if(i > 0.00001 && clr.a > 0.00001) {
					float r=0.0,g=0.0,b=0.0,a=1.0;
					float x1,x2,x3,y1,y2,y3;
					y1 = 1.0;
					y3 = 0.0;
					x2 = i;
					if(i > 0.66666) {
						x1 = 1.0;
						x3 = 0.66666;
						y2 = ( ((x2-x1)*(y3-y1))/(x3-x1) ) + y1;
						r = y2;
						g = 1.0 - r;
					}
					else if(i > 0.33333) {
						x1 = 0.66666;
						x3 = 0.33333;
						y2 = ( ((x2-x1)*(y3-y1))/(x3-x1) ) + y1;
						g = y2;
						b = 1.0 - g;
					}
					else if(i > 0.0) {
						x1 = 0.33333;
						x3 = 0.0;
						y2 = ( ((x2-x1)*(y3-y1))/(x3-x1) ) + y1;
						b = y2;
						a = b;
					}

					// mix with model color
					gl_FragColor = (0.5 + 0.5*(1-a)) * clr + (0.5 * a) * vec4(r, g, b, 1.0);
				}
				else {
					gl_FragColor = clr;
				}
			END
		}
	}
"""

# flag denoting, whether the final output has been captured by the 360 camera rig
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
	viz.link(loader.getAnimationPath(), viz.MainView)

	acc = Accumulator()
	acc.setPosition(viz.MainView.getPosition())

	global _capture_done
	_capture_done = False

	start_time = viz.getFrameTime()

	# update function capturing accumulating view intensity
	def capture(accumulator, player):
		global _capture_done

		if player.isPlaying():
			accumulator.update()
		else:
			if not _capture_done:
				acc.saveAll()
				_capture_done = True
				print "Intensity capture done."

	update = vizact.onupdate(1, capture, acc, player)

def displayHeatmap(project = True):
	'''
	 - Load accumulated view textures
	 - Add cube projector with given textures and shader converting intensities to heat map colors
	 - Let projector affect scene
	'''
	import viz
	import vizact
	import vizcam

	viz.setMultiSample(4)

	viz.go()

	vizcam.WalkNavigate()

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
		
		global _heatmap_shader

		heat_projector = CubeProjectorVizfx(cube_textures, shader_code = _heatmap_shader)
		heat_projector.setPosition(viz.MainView.getPosition())
		heat_projector.affect(piazza)

		def update(hp):
			hp.update()

		vizact.onupdate(0, update, heat_projector)
	else:
		import vizshape

		env = viz.addEnvironmentMap('accumulated.bmp', faces = ['_p_x', '_n_x', '_p_y', '_n_y', '_p_z', '_n_z'])

		sb = vizshape.addSkyBox()
		sb.texture(env)