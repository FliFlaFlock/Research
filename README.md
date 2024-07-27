# Automated_MorphoGraphX_PaCeQuant

# Purpose
<p>This python script automates the cell segmentaion of plant pavement cells using a workflow described in https://doi.org/10.1186/s12915-019-0657-1.</p> 
<p>Specifically, the worklfow automates MorphoGraphX, used to extract only the signal in a certain distance to the cell surface and creates tif files, and PaCeQuant which is a tool for pavement cell segmentation
The script generates many such tif files based on the user's input parameters as descibed below. Among these you can then choose the best segmentation. If the best segmentation is not perfect you can then use MiToBo's tool for manual correction.</p> 
<p>If you wish to auotmate MorphoGraphX with a similar, or even different purpose, I hope this script can still be of use to realize your own script.</p>

# Requirements
<p> <strong>MorphoGraphX 2.0.1</strong> (https://morphographx.org/software/). Tested specifically on the cuda version on Ubuntu 20.04 (mgx-2.0.1-382-ubuntu20.04-cuda). Other versions of 2.0.1 (e.g. without cuda) should also work, but other versions may have different names or parameter structures for the processes used.</p> 
<p> <strong>Python 3.X (tested on 3.8) as well as Python 2.7</strong>. You should run the script using the latest Python version (or 3.8 to be safe). Python 2.7 is required for running python within MorphoGraphX. If under MorphoGraphX under Processes/Misc you do not see a Python tab, you probably have not installed Python 2.7. </p>
<p>This script does not require a local running Fiji version with PaCeQuant. Rather, it makes use of <strong>PyImageJ</strong>, a python library to run ImageJ (https://py.imagej.net/en/latest/index.html). However, if you wish to manually correct the PaCeQuant segmentations, the LabelImageEditor or MiToBo is required (not part of the script). MiToBo can be installed as a Fiji extension or standalone. More information here: https://mitobo.informatik.uni-halle.de/index.php/Main_Page.</p>
<p>Besides PyImageJ, you also need the following Python libraries: <strong>subprocess</strong>, <strong>os</strong>, <strong>tkinter</strong>, <strong>sys</strong>, <strong>numpy</strong>, <strong>json</strong>, <strong>time</strong>, <strong>shutil</strong> and <strong>re</strong>.</p>


# Worklfow 
### Upon Start-Up
<p>When executing the script you will be prompted to select a folder containing your tif files of interest. Afterwards, you need to provide the Gaussian filter radius (in um) as well as the Edge Detect Threshold, used by MorphoGraphX, for each tif file. These values provide the basis of the surface created in MorphoGraphX.</p>
<p>The next window asks you to change the general parameters. You probably won't change most of these, but you probably want to change the Annhiliation Ranges and Range of Tested Annihilations according to your files. More information on this below.</p>
<p>A .py script is created containing all parameters set, and MorphoGraphX is started. As the last manual step, in MorphoGraphX select the python file that was just created in the prior chosen directory using Processes/Misc/Python</p>

### MorphoGraphX: Creates tif files of signal only in a certain distance to the surface
<p>For each tif file the stack is loaded (<strong>Processes/Stack/System/Open</strong>). If you have ticked the box to flip the stack for a specific tif file, the stack will be flipped (<strong>Process/Stack/Canvas/ReverseAxes</strong> with z: yes) Afterwards, the given Gaussian Filter is applied (<strong>Process/Stack/Filters/GaussianBlurStack</strong>) and edge detect is run with the chosen threshold (<strong>Process/Stack/Morphology/EdgeDetect</strong>). Using this, a mesh (aka surface) is created using <strong>Process/Mesh/Creation/MarchingCubesSurface</strong>, smoothed (<strong>Process/Mesh/Structure/SmoothMesh</strong>) and subdivided (<strong>Process/Mesh/Structure/Subdivide</strong>). The main stack (not Gaussed) is then loaded (<strong>Process/Stack/MultiStack/CopyMainToWork</strong>) and the signal with a certain distance to the surface is picked (aka annihilated) using <strong>Process/Stack/MeshInteraction/Annihilate</strong>. Finally, the working stack is copied to the main stack (<strong>Process/Stack/MultiStack/CopyWorkToMain</strong>) and the tif is saved (<strong>Process/Stack/System/Save</strong>).</p>
<p>Note that for each tif input file this workflow is/can be applied with different annihilation parameters. Specifically, the thickness of signal used (dubbed Annihilation Ranges (um), e.g. 2 for a thickness of 2 um) and which range should be tested (dubbed Range of Tested Annihilations (um), e.g. Min: 8.0 and Max: 14.0 -> This would, given an Annihilation Range of 2 um, run the workflow for the followiung annihialtions: 8-10 um, 10-12 um and 12-14 um). Note that you can choose multiple Annihilation Ranges (e.g. 2, 4) to get all tif files in the given Range of Tested Annihilations with thickness of 2 um AND 4 um. Again, if you wish to add another parameter to test for in this workflow, implementation should be rather simple. </p>

### Fiji: used to get rid of some artifacts created when using MorphoGraphX, as well as perform the MAX-z-projection
<p>Once the tif file(s) for each tif input file are aquired Fiji is used (in the form of PyImageJ) to get MAX-z-projections. Before that, however, some artifacts produced by the annihlation function of MorphoGraphX are fixed. The anihilation function does not only "annihilate" form the direction of the upper surface, but from  all around the produced surface. Thus, a bottom layer as well as a border around the whole stack would be MAX-projected. To remove these, a simple cropping (to get rid of the borders, i.e. the projection form the sides) and a duplication of the stack cutting off the bottom based on the annihilation and voxel sizes are performed. Finally, the MAX-z-projection is performed.</p>

### PaCeQuant (Fiji): Segments the cells
PaCeQuant is finally applied on the whole directory (After_MorphoGraphX) containing all output files. Here, the standard settings are used, and no IDs are generated in the resulting image. IDs are not included as they create artifacts when manually correcting the segmentation afterwards with LabelImageEditor from MiToBo. Thus, if you want to have any IDs you can run PaCeQuant manually using the segmentations as input files and check the box to inlcude IDs. This will also re-create the feature inforamtion files (which is relevant if you manually corrected the segmentation; otherwise they are the same of course).


# Sources
<p>MorphoGraphX:</p>
<p>PaCeQuant:</p>
<p>Fiji:</p>
