from observer_projector import *
from texture_projector import *
import vizcam
import vizact

viz.setMultiSample(4)
viz.fov(60)
viz.go()

vizcam.WalkNavigate()

piazza = viz.addChild('piazza.osgb')

render_nodes = {
	viz.POSITIVE_X : viz.addRenderNode(inheritView = False),
	viz.NEGATIVE_X : viz.addRenderNode(inheritView = False),
	viz.POSITIVE_Y : viz.addRenderNode(inheritView = False),
	viz.NEGATIVE_Y : viz.addRenderNode(inheritView = False),
	viz.POSITIVE_Z : viz.addRenderNode(inheritView = False),
	viz.NEGATIVE_Z : viz.addRenderNode(inheritView = False)
}

tex_quads = {
	viz.POSITIVE_X : viz.addTexQuad(),
	viz.NEGATIVE_X : viz.addTexQuad(),
	viz.POSITIVE_Y : viz.addTexQuad(),
	viz.NEGATIVE_Y : viz.addTexQuad(),
	viz.POSITIVE_Z : viz.addTexQuad(),
	viz.NEGATIVE_Z : viz.addTexQuad()
}

cube_textures = {
	viz.POSITIVE_X : viz.addTexture('right.png'),
	viz.NEGATIVE_X : viz.addTexture('left.png'),
	viz.POSITIVE_Y : viz.addTexture('up.png'),
	viz.NEGATIVE_Y : viz.addTexture('down.png'),
	viz.POSITIVE_Z : viz.addTexture('front.png'),
	viz.NEGATIVE_Z : viz.addTexture('back.png')
}

cube_euler = {
	viz.POSITIVE_X : [90,0,0],
	viz.NEGATIVE_X : [-90,0,0],
	viz.POSITIVE_Y : [0,-90,0],
	viz.NEGATIVE_Y : [0,90,0],
	viz.POSITIVE_Z : [0,0,0],
	viz.NEGATIVE_Z : [180,0,0] 
}

projectors = {
	viz.POSITIVE_X : None,
	viz.NEGATIVE_X : None,
	viz.POSITIVE_Y : None,
	viz.NEGATIVE_Y : None,
	viz.POSITIVE_Z : None,
	viz.NEGATIVE_Z : None
}

i = 0
for face in projectors:
	render_nodes[face].setPosition(0,1.8,0)
	render_nodes[face].setEuler(cube_euler[face])
	render_nodes[face].setProjectionMatrix(viz.Matrix.perspective(90.0,1.0,0.1,100.0))
	render_nodes[face].setRenderLimit(viz.RENDER_LIMIT_FRAME)
	render_nodes[face].setRenderTexture(viz.addRenderTexture())
	
	projectors[face] = ObserverProjector(
		cube_textures[face],
		view_node = render_nodes[face]
	)
	projectors[face].setPosition(0,1.8,0)
	projectors[face].setEuler(cube_euler[face])
	projectors[face].affect(render_nodes[face])
	
	tex_quads[face].texture(render_nodes[face].getRenderTexture())
	tex_quads[face].setPosition(i-2.5, 1.8, 3.0)
	tex_quads[face].renderToAllRenderNodesExcept(render_nodes.values())
	i += 1.1

def update():
	global projectors
	for face in projectors:
		projectors[face].update()
	
vizact.onupdate(0, update)