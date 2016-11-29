uniform mat4 tex_ViewMat;
uniform mat4 tex_ProjMat;
uniform mat4 viewMatInverse;

varying vec4 projCoord;
varying vec4 coord;

void main()
{
	// need to project the model into the view of the other frustum
	// model coordinates need to be relative to other projection
	projCoord = tex_ProjMat * tex_ViewMat * viewMatInverse * gl_ModelViewMatrix * gl_Vertex;
	
	gl_FrontColor = gl_Color;
	coord = ftransform();
	gl_Position = ftransform();
}
