varying vec4 projCoord;

uniform sampler2D projectionTex;
uniform sampler2D projectionDepth;

void main (void)
{
	float epsilon = 0.00001;
	vec4 clr = vec4(0.0,0.0,0.0,1.0);
	vec4 dividedCoord = projCoord;
	
	if (dividedCoord.z >= 0.0) {
		dividedCoord /= dividedCoord.w;
		float u = dividedCoord.x * 0.5 + 0.5;
		float v = dividedCoord.y * 0.5 + 0.5;
		float z = dividedCoord.z * 0.5 + 0.5;
		if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
			vec4 depth = texture2D(projectionDepth, vec2(u, v));
			if(z < depth.r+0.0005)
				clr = texture2D(projectionTex, vec2(u, v));
		}					
	}
	
	gl_FragColor = clr;
}
