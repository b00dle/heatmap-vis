// this will change in ver 5 when we can specify matrix uniforms
uniform mat4 mainViewMat_inv;
uniform mat4 viewMat;
uniform mat4 projMat;

uniform mat4 osg_ViewMatrixInverse;

varying vec4 projCoord;

void main()
{
	// need to project the model into the view of the other frustum
	// model coordinates need to be relative to other projection
	projCoord = projMat * viewMat * mainViewMat_inv * gl_ModelViewMatrix * gl_Vertex;
	gl_FrontColor = gl_Color;
	gl_Position = ftransform();
}
