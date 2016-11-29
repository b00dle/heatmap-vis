uniform mat4 tex_ViewMat_PX;
uniform mat4 tex_ViewMat_NX;
uniform mat4 tex_ViewMat_PY;
uniform mat4 tex_ViewMat_NY;
uniform mat4 tex_ViewMat_PZ;
uniform mat4 tex_ViewMat_NZ;

uniform mat4 tex_ProjMat;
uniform mat4 osg_ViewMatrixInverse;

varying vec4 projCoord_PX;
varying vec4 projCoord_NX;
varying vec4 projCoord_PY;
varying vec4 projCoord_NY;
varying vec4 projCoord_PZ;
varying vec4 projCoord_NZ;

void main()
{
	// need to project the model into the view of the other frustum
	// model coordinates need to be relative to other projection
	projCoord_PX = tex_ProjMat * tex_ViewMat_PX * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	projCoord_NX = tex_ProjMat * tex_ViewMat_NX * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	projCoord_PY = tex_ProjMat * tex_ViewMat_PY * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	projCoord_NY = tex_ProjMat * tex_ViewMat_NY * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	projCoord_PZ = tex_ProjMat * tex_ViewMat_PZ * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	projCoord_NZ = tex_ProjMat * tex_ViewMat_NZ * osg_ViewMatrixInverse * gl_ModelViewMatrix * gl_Vertex;
	
	gl_FrontColor = gl_Color;
	gl_Position = ftransform();
}
