varying vec4 projCoord_PX;
varying vec4 projCoord_NX;
varying vec4 projCoord_PY;
varying vec4 projCoord_NY;
varying vec4 projCoord_PZ;
varying vec4 projCoord_NZ;

uniform sampler2D projectionTex_PX;
uniform sampler2D projectionTex_NX;
uniform sampler2D projectionTex_PY;
uniform sampler2D projectionTex_NY;
uniform sampler2D projectionTex_PZ;
uniform sampler2D projectionTex_NZ;

void main (void)
{
	gl_FragColor = (0, 0, 0, 0);
	
	vec4 dividedCoord = projCoord_PX;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_PX, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
	
	dividedCoord = projCoord_NX;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_NX, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
	
	dividedCoord = projCoord_PY;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_PY, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
	
	dividedCoord = projCoord_NY;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_NY, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
	
	dividedCoord = projCoord_PZ;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_PZ, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
	
	dividedCoord = projCoord_NZ;
	
	if (dividedCoord.z >= 0)
	{
		dividedCoord /= dividedCoord.w;
		//dividedCoord /= dividedCoord.z;
		gl_FragColor += texture2D(projectionTex_NZ, (dividedCoord.st*0.5 + vec2(0.5, 0.5)));
	}
}
