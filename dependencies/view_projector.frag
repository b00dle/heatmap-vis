varying vec4 projCoord;

uniform sampler2D depth_tex;
uniform sampler2D prev_frame_tex;
uniform float frame_weight;
uniform float aperture_scale;

void main (void)
{
	vec4 dividedCoord = projCoord;
	
	gl_FragColor = vec4(0, 0, 0, 1.0);
	
	// init color to match last frames projection
	// new color will be added on top
	vec4 lastColor;
	lastColor.rgb = texture2D(prev_frame_tex, gl_FragCoord.xy/1024.0);
	gl_FragColor.rgb = lastColor.rgb;
	
	dividedCoord /= dividedCoord.w;
	if (dividedCoord.z >= 0)
	{
		// calc texture coords from reprojected fragment coordinate
		float u =  dividedCoord.x * 0.5 + 0.5f;
		float v =  dividedCoord.y * 0.5 + 0.5f;
		// normalize z for depth test
		float z =  dividedCoord.z * 0.5 + 0.5f;
		
		// get the depth buffer and test against that (INVERSE SHADOW MAPPING)
		vec4 depthColor = texture2D(depth_tex, vec2(u,v));
		
		// color only if normalized z is closer than depth
		if (z < depthColor.r + 0.005)
		{
			// calculate distance factor from aperture_scale
			float dist_scale = aperture_scale + (1-aperture_scale)*10.0;
			
			// sample from the distance into the camera to get gaussian
			// and apply additional scaling
			float intensity = 1.0 - min(1.0, length(dividedCoord.xy)*dist_scale);
			intensity *= 0.1 * (frame_weight + (1-frame_weight)*0.1);
			
			// project intensity
			gl_FragColor += vec4(intensity, intensity, intensity, 1.0);
		}
	}
	
	// set alpha to 1 to avoid artifacts
	gl_FragColor.a = 1.0;
}
