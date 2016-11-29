varying vec4 projCoord;
varying vec4 observerCoord;

uniform sampler2D projectionTex;
uniform sampler2D projectionDepth;
uniform sampler2D observerDepth;

vec4 observedClr(float offset) {
	float epsilon = 0.00001;
	vec4 clr = vec4(0.0);
	vec4 dividedCoord = observerCoord;
	
	if(dividedCoord.z > 0) {
		dividedCoord /= dividedCoord.w;
		float dist = length(dividedCoord.xy);
		float u = dividedCoord.x * 0.5 + 0.5;
		float v = dividedCoord.y * 0.5 + 0.5;
		float z = dividedCoord.z * 0.5 + 0.5;
		if(abs(u - clamp(u, 0.0, 1.0)) < epsilon && abs(v - clamp(v, 0.0, 1.0)) < epsilon) {
			vec4 depth = texture2D(observerDepth, vec2(u, v));
			if(z < depth.g+0.0005 && dist < offset) {
				float i = 1-(dist/offset);
				i = max(0.01, i);
				clr = vec4(i,i,i,1.0);
			}
		}
	}
	
	return clr;
}

vec4 projectedClr(void) {
	float epsilon = 0.00001;
	vec4 clr = vec4(0.0);
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
	
	return clr;
}

void main (void)
{
	vec4 clr = vec4(0.0,0.0,0.0,1.0);
	
	// add color computed by uniform observer view direction
	//clr += 0.05 * observedClr(0.05);
	clr = observedClr(0.05);
	
	// add projected color
	// if statement checks for alpha texture value
	// which has to be disregarded
	vec4 projClr = projectedClr();
	if(projClr.a > 0.00000001)
		clr += projClr;
	
	// set final color
	gl_FragColor = vec4(min(clr.r,1.0), min(clr.g,1.0), min(clr.b,1.0), 1.0);
}
