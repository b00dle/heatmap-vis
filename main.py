from heatmap import *

# 1.) create a view animation file
# 	- press 'r' to toggle recording

#recordViewAnimation()

# 2.) accumulate view intensities
#   - wait until animation path is played back completely
#   - output 'Intensity capture done.' signals when textures have been generated.

#captureViewIntensity()

# 3.) render heatmap based on view intensities
#   - choose project = True to display heatmap projected onto geometry
#   - choose project = False to view environment map of intensity values (greyscale)

displayHeatmap(project = True)