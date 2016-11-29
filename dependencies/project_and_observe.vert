uniform mat4 tex_ViewMat;
uniform mat4 tex_ProjMat;

uniform mat4 viewMatInverse;

uniform mat4 observer_ViewMat;
uniform mat4 observer_ProjMat;

varying vec4 projCoord;
varying vec4 observerCoord;

void main()
{
	// original approach
	//mat4 model_mat = viewMatInverse * gl_ModelViewMatrix;
	// modified approach
	mat4 model_mat = inverse(tex_ViewMat) * /*viewMatInverse */ gl_ModelViewMatrix;
	
	// need to project the model into the view of the other frustum
	// model coordinates need to be relative to other projection
	// modified approach
	projCoord = tex_ProjMat * gl_ModelViewMatrix * gl_Vertex;
	// original approach
	//projCoord = tex_ProjMat * tex_ViewMat * model_mat * gl_Vertex;
	
	// compute screen position of main view coord
	observerCoord = observer_ProjMat * observer_ViewMat * model_mat * gl_Vertex;
	
	gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
}
