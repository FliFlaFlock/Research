import subprocess
import os
import tkinter.filedialog
import tkinter as tk
import sys
import numpy as np
import json
import time
import shutil
import re
import imagej

# gives PyImageJ more memory
jvm_options = [
    '-Xms2g',  # initial 2 GB
    '-Xmx8g'   # max 8 GB
]


def get_files(path):
    """
    Returns all .tif files as strings in a given directory
    Additionally renames files if they contain spaces
    :param path: input directory (path as string)
    :return: list of strings (of .tif file names)
    """
    list = []
    for file in os.listdir(path):
        stripped_file = re.sub(r'\s+', '', file)

        # check for spaces in file name
        if file != stripped_file:
            unstripped_path = os.path.join(path, file)
            stripped_path = os.path.join(path, stripped_file)
            try:
                os.rename(unstripped_path, stripped_path)
                print(f"Renamed: '{unstripped_path}' -> '{stripped_path}'")
            except OSError as e:
                print(f"Error renaming file '{unstripped_path}' to '{stripped_path}': {e}")
            file = stripped_file

        file_name, file_extension = os.path.splitext(file)

        if os.path.isfile(os.path.join(path, file)) and file_extension == ".tif":
            list.append(file)

    if not list:  # check that the list is not empty
        tk.messagebox.showerror("Input Error", "Folder Does not Contain any .tif Files")
        sys.exit()
    else:
        return list


class AskTG:
    """Asks user for Gaussian Radius and Edge Detect Threshold for each .tif

    Creates a tkinter window which asks the users input for each file in a list of strings (i.e. the .tif file names).
    Checks whether all values are filled out and are either an integer or float.
    Output: Array of Gaussian Radii and Edge Detect Thresholds for each file
            List of either 0 and 1's for the flip-stack parameter

    attributes:
        root: tkinter window
        list: list of strings
        values: array to be filled with tkinter entries for Gaussian Radii and Edge Detect Thresholds for each string
        values_saved: array to be filled with Gaussian Radii and Edge Detect Thresholds for each string in list
        flips: list to be filled with tkinter entries whether to flip the stack or not (button)
        flips_saved: list to be filled with whether to flip the stack or not (in the form of 0's and 1's)
    """
    def __init__(self, root, list):
        """Initializes Variables, creates tkinter layout"""
        self.root = root
        self.values = []
        self.values_saved = []
        self.flips = []
        self.flips_saved = []

        # Headers
        gauss_header = tk.Label(root, text="Radius for Gaussian (um)")
        gauss_header.grid(row=0, column=1, padx=5, pady=5)

        edge_threshold_header = tk.Label(root, text="Threshold for Edge Detect")
        edge_threshold_header.grid(row=0, column=2, padx=5, pady=5)

        flip_header = tk.Label(root, text="Flip Stack?")
        flip_header.grid(row=0, column=3, padx=5, pady=5)

        # Create a row in tkinter for each file in list
        for i in range(0, len(list)):
            file = tk.Label(root, text=list[i])
            file.grid(row=i+1, column=0, padx=10, pady=10)
            gauss = tk.Entry(root)
            gauss.grid(row=i+1, column=1, padx=5, pady=5)
            edge_threshold = tk.Entry(root)
            edge_threshold.grid(row=i+1, column=2, padx=5, pady=5)
            self.values.append((gauss, edge_threshold))

            flip = tk.IntVar()
            tk.Checkbutton(root, variable=flip, onvalue=1, offvalue=0).grid(row=i+1, column=3, padx=5, pady=5)
            self.flips.append(flip)

        # button that calls save_and_close when pressed
        save_button = tk.Button(root, text="Confirm", command=self.save_and_close)
        save_button.grid(row=len(list) + 1, column=0, columnspan=3, pady=10)

    def save_values(self):
        """Saves values of tkinter entries"""
        self.values_saved = [[Gauss.get(), Edge_T.get()] for Gauss, Edge_T in self.values]
        self.flips_saved = [flip.get() for flip in self.flips]

    def save_and_close(self):
        """Error management, calls check_if_number and check_entries"""
        if self.check_entries():
            if self.check_if_number():
                self.save_values()
                self.root.destroy()
            else:
                tk.messagebox.showerror("Input Error", "Please Only Input Floats or Integers")
        else:
            tk.messagebox.showerror("Input Error", "Please Leave No Parameter Empty")

    def check_if_number(self):
        """Checks whether entries are numbers"""
        for gauss, edge_threshold in self.values:
            if not self.is_number(gauss.get()) or not self.is_number(edge_threshold.get()):
                return False
        return True

    def check_entries(self):
        """Checks whether all tkinter entries are filled"""
        for gauss, edge_threshold in self.values:
            if not gauss.get() or not edge_threshold.get():
                return False
        return True

    @staticmethod
    def is_number(value):
        """Checks whether entries are numbers"""
        try:
            float(value)
            return True
        except ValueError:
            return False


class CheckParameters:
    """Asks user for general MorphoGraphX parameters

    Creates a tkinter window with prefilled parameters that the user can change
    Checks whether all values are filled out and are either an integer or float.
    Output: Lists of parameters (split in two; one for the button, i.e. yes/no parameters, and one for the others)

    attributes:
        root: tkinter window

        parameter_labels: tkinter names for the parameters
        parameters_initial: initial values of parameters
        parameters: list to be filled with tkinter entries for the parameters
        parameters_saved: final values of parameters

        annihilate_ranges_label: label for Annihilation Ranges parameters for tkinter
        annihilate_ranges_initial: initial value of Annihilation Ranges parameter
        annihilate_ranges: tkinter entry for the Annihilation Ranges parameter
        annihilate_ranges_saved: final value of Annihilation Ranges parameter

        flip_labels: tkinter names for the button parameters (i.e. 'Smooth Mesh: Walls Only?' and 'Annihilate: Fill?')
        flips: list to be filled with tkinter entries for the button parameters
        flips_saved: final values for button parameters
    """
    def __init__(self, root):
        self.root = root
        self.parameter_labels = [
            'Range of Tested Annihilations (um)', 'Range of Tested Annihilations_max (um)',
            'Edge Detect Multiplier',
            'Edge Detect Adaptive Factor',
            'Edge Detect Fill Value',
            'Marching Cubes Surface Radius (um)',
            'Marching Cubes Surface Threshold',
            'Number of Smooth Mesh Passes',
            'Annihilate Fill Value'
        ]
        self.parameters_initial = [
            6.0, 20.0, 2.0, 0.3, 30000, 5.0, 5000, 1, 30000
        ]
        self.parameters = []
        self.parameters_saved = []

        self.annihilate_ranges_label = 'Annihilation Ranges (um)'
        self.annihilate_ranges_initial = '2, 4'
        self.annihilate_ranges = []
        self.annihilate_ranges_saved = []

        self.flip_labels = ['Smooth Mesh: Walls Only?', 'Annihilate: Fill?']
        self.flips = []
        self.flips_saved = []

        # create the tkinter window with prefilled values for general parameters
        for i in range(0, len(self.parameters_initial)-2):
            if i == 0:
                often_changing_pars = tk.Label(root, text="Typically Changed Par")
                often_changing_pars.grid(row=i, column=1, padx=10, pady=10)

                annihilate_ranges_lab = tk.Label(root, text=self.annihilate_ranges_label)
                annihilate_ranges_lab.grid(row=i + 1, column=0, padx=10, pady=10)
                annihilate_ranges = tk.Entry(root)
                annihilate_ranges.insert(0, self.annihilate_ranges_initial)
                annihilate_ranges.grid(row=i + 1, column=1, padx=5, pady=5)
                self.annihilate_ranges = annihilate_ranges

                annihilate_range_lab = tk.Label(root, text=self.parameter_labels[i])
                annihilate_range_lab.grid(row=i+2, column=0, padx=10, pady=10)
                annihilate_min_min = tk.Entry(root)
                annihilate_min_min.insert(0, self.parameters_initial[i])
                annihilate_min_min.grid(row=i+2, column=1, padx=5, pady=5)
                annihilate_max_max = tk.Entry(root)
                annihilate_max_max.insert(0, self.parameters_initial[i+1])
                annihilate_max_max.grid(row=i+2, column=2, padx=5, pady=5)
                self.parameters.append(annihilate_min_min)
                self.parameters.append(annihilate_max_max)
                usually_unchanging_pars = tk.Label(root, text="Usually unchanged Pars")
                usually_unchanging_pars.grid(row=i+3, column=1, padx=10, pady=10)
            file = tk.Label(root, text=self.parameter_labels[i+2])
            file.grid(row=i+3, column=0, padx=10, pady=10)
            value = tk.Entry(root)
            value.insert(0, self.parameters_initial[i+2])
            value.grid(row=i+3, column=1, padx=5, pady=5)
            self.parameters.append(value)

        # expand the tkinter window with button parameters
        for i in range(0, len(self.flip_labels)):
            file = tk.Label(root, text=self.flip_labels[i])
            file.grid(row=len(self.parameter_labels) + i + 3, column=0, padx=10, pady=10)
            flip = tk.IntVar()
            tk.Checkbutton(root, variable=flip, onvalue='Yes', offvalue='No').grid(row=len(self.parameter_labels) + i + 3, column=1, padx=5, pady=5)
            self.flips.append(flip)

        save_button = tk.Button(root, text="Confirm", command=self.save_and_close)
        save_button.grid(row=len(self.parameter_labels) + len(self.flip_labels) + 3, column=0, columnspan=3, pady=10)

    def save_values(self):
        """Saves values of tkinter entries"""
        self.parameters_saved = [par.get() for par in self.parameters]
        self.flips_saved = [flip.get() for flip in self.flips]
        self.annihilate_ranges_saved = self.annihilate_ranges.get()

    def save_and_close(self):
        """Error management, calls check_if_number and check_entries"""
        if self.check_entries():
            if self.check_if_number():
                self.save_values()
                self.root.destroy()
            else:
                tk.messagebox.showerror("Input Error", "Please Only Input Floats or Integers")
        else:
            tk.messagebox.showerror("Input Error", "Please Leave No Parameter Empty")

    def check_entries(self):
        """Checks whether all tkinter entries are filled"""
        for par in self.parameters:
            if not par.get():
                return False
        return True

    def check_if_number(self):
        """Checks whether entries are numbers"""
        for par in self.parameters:
            if not self.is_number(par.get()):
                return False
        return True

    @staticmethod
    def is_number(value):
        """Checks whether entries are numbers"""
        try:
            float(value)
            return True
        except ValueError:
            return False


window_askTG = tk.Tk()
window_askTG.title("Give Gaussian and Edge Threshold Values For Each File")
window_askTG.resizable(width=False, height=False)

# Ask user for Directory and check whether it contains .tif files. If so, save the names in a list
Dir_Tifs = tk.filedialog.askdirectory(mustexist=tk.TRUE)
MGX_Tifs_In = get_files(Dir_Tifs)

# get Gaussian Radii, Edge Detect Thresholds and whether to flip the stack for each file
instance = AskTG(window_askTG, MGX_Tifs_In)
window_askTG.mainloop()
collected_values = np.asarray(instance.values_saved)
flip_list = list(map(str, instance.flips_saved))
if collected_values.size == 0:
    sys.exit()


window_ask_pars = tk.Tk()
window_ask_pars.title("Choose Parameters")
window_ask_pars.resizable(width=False, height=False)

# get global MorphoGraphX parameters
check_pars = CheckParameters(window_ask_pars)
window_ask_pars.mainloop()
collected_parameters = [check_pars.annihilate_ranges_saved] + check_pars.parameters_saved + list(map(str, check_pars.flips_saved))
variable_name_list = [check_pars.annihilate_ranges_label] + check_pars.parameter_labels + check_pars.flip_labels
if not collected_parameters:
    sys.exit()


def get_standalone_pars(variable_names, variables):
    dic = dict(zip(variable_names, variables))
    return dic


dictionary_collected_parameters = get_standalone_pars(variable_name_list, collected_parameters)

# create a new python file (2.7) which should be executed via MGX
new_python_file = open(Dir_Tifs + '/' + "MGX_python_script.py", "w")
new_python_file_content_list = ['import os',
                                'import json',
                                '# Settings',
                                '# --------------------------------------------------------------------',
                                'path_in = "' + Dir_Tifs + '/" #File path',
                                '# Settings that are always changed',
                                '# Step1: Check whether your stack has to be flipped (depends on imaging direction). ' +
                                'In order to check, simply drag and drop the stack into MorphoGraphX. ' +
                                'If the surface is facing towards you (upward) then it is already correct, ' +
                                'i.e. you do not have to flip the stack.',
                                '# Step2: Manually (!) check a fitting Gaussian value and Edge_T that does neither ' +
                                'result in holes (typically due to too high Edge_T) or peaks ' +
                                '(typically due to low Edge_T; can be reduced by increasing Gaussian)',
                                '# Step3: Pick the range of annihilation distances used as well as how thick each ' +
                                'annihilation should be. This program will then check ' +
                                'various combinations. Example, Annihilate_MinMin = 6.0 and Annihilate_MaxMax = ' +
                                '12.0 and delta_annihilate = [2, 4]: Annihilations 6-8, 6-10, 8-10, 8-12, 10-12 are ' +
                                'checked. Note, that the FIRST annihilate_delta value is used for the interval of ' +
                                'used stacks (e.g. when 12-16 should it go to 14-18 (value of 2) or ' +
                                '16-18 (value of 4))',
                                'files = ["' + '", "'.join(MGX_Tifs_In) + '"]',
                                'flip_stack = ["' + '", "'.join(flip_list) + '"] #True if the stack has to ' +
                                'be flipped, i.e. Stack/Canvas/ReverseAxes is applied for each file ' +
                                '(0 = false, 1 = true)',
                                'gaussian = ["' + '", "'.join(collected_values[:, 0]) + '"] # radius of gaussian ' +
                                'filter in um (Stack/Filters/GaussianBlurStack); same for x, y and z',
                                'edge_threshold = ["' + '", "'.join(collected_values[:, 1]) + '"] #Threshold of ' +
                                'Stack/Morphology/EdgeDetect',
                                'delta_annihilate = ' +
                                '[' + dictionary_collected_parameters['Annihilation Ranges (um)'] + '] ' +
                                '# List of checked annihilation distances. For [2,4] it will check 6-8 and 6-10 ' +
                                'annihilation for example',
                                'annihilate_min_min = "' +
                                '' + dictionary_collected_parameters['Range of Tested Annihilations (um)'] + '" ' +
                                '#Lowest value of annihilation ranges used (in um) for ' +
                                'Stack/MeshInteraction/Annihilate',
                                'annihilate_max_max = "' +
                                '' + dictionary_collected_parameters['Range of Tested Annihilations_max (um)'] + '' +
                                '" #Highest value of annihilation ranges used (in um) for ' +
                                'Stack/MeshInteraction/Annihilate',
                                '# Settings that are usually the same (standard MGX values)',
                                'edge_mult = "' + dictionary_collected_parameters['Edge Detect Multiplier'] + '' +
                                '" #Multiplier of Stack/Morphology/EdgeDetect',
                                'edge_adapt= "' + dictionary_collected_parameters['Edge Detect Adaptive Factor'] + '' +
                                '" #Adaptive Factor for threshold of Stack/Morphology/EdgeDetect',
                                'edge_fill_val= "' + dictionary_collected_parameters['Edge Detect Fill Value'] + '' +
                                '" #Fill Value of Stack/Morphology/EdgeDetect',
                                'marching_cubes_surface_cube_size = "' +
                                '' + dictionary_collected_parameters['Marching Cubes Surface Radius (um)'] + '' +
                                '" #Cube Size in um for ' +
                                'Mesh/Creation/MarchingCubesSurface',
                                'marching_cubes_surface_threshold = "' +
                                '' + dictionary_collected_parameters['Marching Cubes Surface Threshold'] + '' +
                                '" #Threshold for Mesh/Creation/MarchingCubesSurface',
                                'smooth_mesh_passes = "' +
                                '' + dictionary_collected_parameters['Number of Smooth Mesh Passes'] + '' +
                                '" #Passes for Mesh/Structure/SmoothMesh',
                                'smooth_mesh_walls_only = "' +
                                '' + dictionary_collected_parameters['Annihilate Fill Value'] + '' +
                                '" #Walls Only for Mesh/Structure/SmoothMesh',
                                'annihilate_fill = "' +
                                '' + dictionary_collected_parameters['Smooth Mesh: Walls Only?'] + '' +
                                '" #Should Signal be overwritten with a certain value ' +
                                '(Annihilate_FillVal); Stack/MeshInteraction/Annihilate; usually not used ' +
                                'as Fill = False',
                                'annihilate_fill_val = "' + dictionary_collected_parameters['Annihilate: Fill?'] + '' +
                                '" #Fill Value for Stack/MeshInteraction/Annihilate; ' +
                                'usually not used as Fill = False',
                                'file_annihilation_dictionary = []',
                                '# MorphoGraphX Workflow',
                                'def mgx_workflow(file, flip, gauss, edge_threshold):',
                                '    tif_path = path_in + file',
                                '    tif_out = path_in + "/After_MorphoGraphX/" + file',
                                '    os.mkdir(tif_out)',
                                '    for annihilate_range in delta_annihilate:',
                                '        current_min = annihilate_min_min',
                                '        while float(current_min) < float(annihilate_max_max):',
                                '            Process.Stack__System__Open(tif_path, "Main", "0", "", "Yes")',
                                '            if flip == "1":',
                                '                Process.Stack__Canvas__Reverse_Axes("No", "No", "Yes")',
                                '            Process.Stack__Filters__Gaussian_Blur_Stack(gauss, gauss, gauss)',
                                '            Process.Stack__Morphology__Edge_Detect(edge_threshold, edge_mult, ' +
                                'edge_adapt, edge_fill_val)',
                                '            Process.Mesh__Creation__Marching_Cubes_Surface' +
                                '(marching_cubes_surface_cube_size, marching_cubes_surface_threshold)',
                                '            Process.Mesh__Structure__Smooth_Mesh(smooth_mesh_passes, ' +
                                'smooth_mesh_walls_only)',
                                '            Process.Mesh__Structure__Subdivide()',
                                '            Process.Stack__MultiStack__Copy_Main_to_Work_Stack()',
                                '            current_max = str(float(current_min) + float(annihilate_range))',
                                '            Process.Stack__Mesh_Interaction__Annihilate(annihilate_fill, ' +
                                'annihilate_fill_val, current_min, current_max)',
                                '            Process.Stack__MultiStack__Copy_Work_to_Main_Stack()',
                                '            new_tif = "annihilation_" + current_min + "-" + ' +
                                'current_max + "_Gauss" + gauss + "_T" + edge_threshold + "_" + file + ".tif"',
                                '            Process.Stack__System__Save(tif_out + "/" + new_tif, ' +
                                '"Main", "0", "5", "/label")',
                                '            current_min = str(float(current_min) + delta_annihilate[0])',
                                '            file_annihilation_dictionary.append({new_tif: current_max})',
                                'os.mkdir(path_in + "After_MorphoGraphX")',
                                'for i in range(0, len(files)):',
                                '    mgx_workflow(files[i], flip_stack[i], gaussian[i], edge_threshold[i])',
                                '    os.remove(path_in + "/After_MorphoGraphX/" + files[i] + "/MorphoGraphX.py")',
                                'with open(path_in + "/file.txt","w") as file:',
                                '    json.dump(file_annihilation_dictionary, file)'
                                ]
for line in new_python_file_content_list:
    new_python_file.write(line + '\n')
new_python_file.flush()

file_annihilate_dictionary_text_file_path = Dir_Tifs + "/file.txt"

# check whether the json txt file is already there (and delete it if it is)
if os.path.exists(file_annihilate_dictionary_text_file_path):
    os.remove(file_annihilate_dictionary_text_file_path)

# check whether the output directory is already there (and delete it if it is)
if os.path.exists(Dir_Tifs + "/After_MorphoGraphX"):
    shutil.rmtree(Dir_Tifs + "/After_MorphoGraphX")

subprocess.run(['mgx', '--model', '"' + Dir_Tifs + '/MGX_python_script.py' + '"'])

# wait for the dictionary to be created in the mgx_py file
while not os.path.exists(file_annihilate_dictionary_text_file_path):
    time.sleep(1)

with open(file_annihilate_dictionary_text_file_path) as f:
    json_string = json.load(f)
annihilation_max_values_dictionary = {key: float(value) for file in json_string for key, value in file.items()}

# ImageJ Workflow: Trim edges, trim bottom and save MAX_z_proj
ij = imagej.init('sc.fiji:fiji:2.14.0')
print(f"ImageJ version: {ij.getVersion()}")

for file in MGX_Tifs_In:
    stacks_path = Dir_Tifs + "/After_MorphoGraphX/" + file
    processed_stacks = get_files(stacks_path)
    for stack in processed_stacks:
        file_path = stacks_path + "/" + stack
        macro = f"""
        file_path = "{file_path}";
        print(file_path);
        max_annihilation = {annihilation_max_values_dictionary[stack]};
        open(file_path);
        getVoxelSize(px_width, px_height, px_depth, unit);
        max_px_width = max_annihilation / px_width;
        max_px_height = max_annihilation / px_height;
        max_px_depth = max_annihilation / px_depth;
        width = getWidth();
        height = getHeight();
        rectangle_x = round(max_px_height) + 1;
        rectangle_y = round(max_px_width) + 1;
        rectangle_width = width - (2 * rectangle_x);
        rectangle_height = height - (2 * rectangle_y);
        makeRectangle(rectangle_x, rectangle_y, rectangle_width, rectangle_height);
        run("Crop");
        trim_amount = round(max_px_depth) + 2;
        number_slices = nSlices();
        run("Duplicate...", "duplicate range=" + trim_amount + "-" + number_slices);
        //saveAs("Tiff", file_path + "_before_projection"); //if you want to check if trimming bottom + edges worked
        run("Z Project...", "projection=[Max Intensity]");
        saveAs("Tiff", file_path);
        run("Close All");
        """
        ij.py.run_macro(macro)

