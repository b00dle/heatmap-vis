varying vec4 projCoord;
varying vec4 coord;

void main (void)
{
	vec4 p = coord;
	p /= p.w;
	vec2 t = (p.st*0.5 + vec2(0.5, 0.5));
	gl_FragColor = vec4(p.z, p.z, p.z, 1.0);//vec4(p.z/p.w,p.z/p.w,p.z/p.w,1.0);
	
/*	
	if (p.z > 0)
	{
		//p /= p.w;
		vec2 tex_c = p.st * 0.5 + vec2(0.5);
		gl_FragColor = vec4(p.z, p.z, 1.0, 1.0);
		//gl_FragColor = vec4(1.0,0.0,0.0,1.0);
	}
	else
		gl_FragColor = (0, 0, 0, 1.0);
*/
}
