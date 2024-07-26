# Automated_MorphoGraphX_PaCeQuant

# Purpose
<p>This python script automates the cell segmentaion of plant pavement cells.</p> 
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

### MorphoGraphX: Creates tif files of signal only in a certain distance to the surface
<p>Each tif file</p>

### Fiji: used to get rid of some artifacts created when using MorphoGraphX, as well as perform the MAX-z-projection

### PaCeQuant (Fiji): Segments the cells

### (optional) Manual Correction (MiToBo via Fiji)


# Sources
MorphoGraphX: 
PaCeQuant:
Fiji:
