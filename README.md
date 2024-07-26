# Automated_MorphoGraphX_PaCeQuant

# Purpose
This python script automates the cell segmentaion of plant pavement cells.
Specifically, the worklfow is a automates MorphoGraphX, used to extract only the signal in a certain distance to the cell surface and creates tif files, and PaCeQuant which is a tool for pavement cell segmentation.
The script generates many such tif files based on the user's input parameters as descibed below. Among these you can then choose the best segmentation. If the best segmentation is not perfect you can then use MiToBo's tool for manual correction. If you wish to auotmate only MorphoGraphX with a similar, or even different purpose, I hope this script can still be of use.

# Requirements



# Worklfow 
1. MorphoGraphX: Creates tif files of signal only in a certain distance to the surface
3. Fiji: used to get rid of some artifacts created when using MorphoGraphX, as well as perform the MAX-z-projection
4. PaCeQuant (Fiji): Segments the cells
5. (optional) Manual Correction (MiToBo via Fiji)

# Sources
MorphoGraphX: 
PaCeQuant:
Fiji:
