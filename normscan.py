from ast import Pass
from optparse import Values
from matplotlib.colors import Normalize
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import math
from collections import Counter
from plyfile import PlyData, PlyElement
import tkinter as tk     # from tkinter import Tk for Python 3.x
import tkinter.filedialog as fd # askopenfilename
import pandas as pd
import argparse
import open3d as o3d
import itertools
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import multiprocessing
from decimal import Decimal


#get some information from user about what kind of experiment they want to run
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--phi", help = "phi value",  type = float,default = 2)
parser.add_argument("-t", "--theta", help = "theta value",  type = float,default = 2)
parser.add_argument("-d", "--density", help = "point cloud density", type = int,default = 100000)

args = parser.parse_args()

density = args.density

"set these as 0 all the time. If desired can change here, but safe bet to use here"
sig_phi = 0
sig_theta = 0

start = time.time()


"ASK USER TO SELECT PLY FILE"
def fileSelect():
    root = tk.Tk()
    files = fd.askopenfilenames(parent=root, title='Choose a file')
    file_list = list(files)
    print(file_list)
    return (file_list)

"CONVERT PLY FILE TO POINT CLOUD. highlighted regions (in some form) allow for stl as input. In final product should use those"
def convertFile(file, density):
    # mesh = o3d.io.read_triangle_mesh(file,density)
    # pointcloud = mesh.sample_points_poisson_disk(density)
    print(file)
    name = file[:-4]
    # print(name)
    print('MADE IT')
    # o3d.io.write_point_cloud(name+".ply", pointcloud)
    plydata = PlyData.read(f'{name}.ply')
    x = np.asarray(plydata.elements[0].data['x'])
    y = np.asarray(plydata.elements[0].data['y'])
    z = np.asarray(plydata.elements[0].data['z'])
    data = np.stack([x,y,z], axis=1)
    point_cloud_array = np.array(data)
    # open3DPick(point_cloud_array)
    # print(point_cloud_array.shape)
    point_cloud_list = point_cloud_array.tolist()
    return (point_cloud_array, point_cloud_list)

"prompt user to select point or range of points and return index of point"
def getData(structure, data):
    #give user some instructions
    print ("!!!!!!!!!!READ ME: THIS IS THE SELECTION SEQUENCE FOR THE " + structure +" !!!!!!!!!!!!")
    print ("Please select a SINGLE point to denote the " + structure +".  Hold down LMB + SHIFT to select point" )
    print ("Hold down RMB + SHIFT to deselect point")
    index = open3DPick(data)
    return (index)
    
"pick points in open 3D or open visualizer to see an interactive point cloud. Took from internet so maybe could be better"
def open3DPick(data):    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(data)
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.run()  
    vis.destroy_window()
    index = vis.get_picked_points()
    return (index)

"following two functions used by math formula to get theta and phi. return 0 if no radius value"
def divisionPhi(n, d):
    return math.atan(n/d)if d else 0

def divisionTheta(n, d):
    return math.acos(n/ d)if d else 0

"Calculate theta and phi and radius valuse from basion (0,0,0) to all points and store in standard format (x,y,z,r,phi,theta)"
def doMath(list_of_coords):
    returnList = []
    for coord in list_of_coords: 
        temp = []
        temp.append(coord[0])
        temp.append(coord[1])
        temp.append(coord[2])
        radius1 = math.sqrt(coord[0]**2 + coord[1]**2 + coord[2]**2)
        phi_rad = divisionPhi(coord[1], coord[0])
        theta_rad = divisionTheta(coord[2],radius1)
        phi_deg = math.degrees(phi_rad)
        theta_deg = math.degrees((theta_rad))
        temp.append(radius1)
        temp.append(theta_deg)
        temp.append(phi_deg)
        returnList.append(temp)
    return (returnList)

"GET ANGLE FOR Z AXIS ROTATION"
def getAngle_Z(xyz_list):
    #get rotation angle using tan inverse of y/x
    angle = math.atan(xyz_list[1]/xyz_list[0]) #is in radians
    rot_angle = (math.pi - angle)
    return (rot_angle)

"only use this ot get xyz list of values when moving poreon. probably a clunky way of doing this"
def fixPoreon(transformList, angle):
    ## Solve for new x and y values for all values
    for data in transformList:
        x = math.cos(angle) * data[0] - data[1] * math.sin(angle)
        y = data[1] * math.cos(angle) + data[0] * math.sin(angle)
        data[0] = x
        data[1] = y
    return(transformList)

"GET ANGLE FOR X AXIS ROTATION FOR NASEON"
def getAngle_X(xyz_list):
    # get angle to rotate whole skull from the naseon now
    print(xyz_list)
    angle_naseon = math.atan(xyz_list[0][2]/xyz_list[0][1]) #is in radians
    #NEED TO IMPLEMENT A CHECKPOINT HERE TO MAKE SURE THAT THIS WORKS EVERY TIME #
    rot_angle_naseon = (-1*angle_naseon)
    return(rot_angle_naseon)

"orient the nasion"
def fixNaseon(trans_rotate_list, angle):
    for data in trans_rotate_list:
        y = data[1] * math.cos(angle) - data[2] * math.sin(angle)
        z = math.sin(angle) * data[1] + data[2] * math.cos(angle)
        data[1] = y
        data[2] = z
    return(trans_rotate_list)

"GET ANGLE OF ROTATION AROUND Y AXIS FOR BASION"
def getAngle_Y(xyz_list):
    # get angle to rotate whole skull from the naseon now
    angle_naseon = math.atan(xyz_list[0][2]/xyz_list[0][0]) #is in radians
    rot_angle_naseon = (-1*angle_naseon)
    return(rot_angle_naseon)

"orient the basion"
def fixBasion(list, angle):
    # Solve for new values using that angle and system of equations
    for data in list:
        x = data[2] * math.sin(angle) + data[0] * math.cos(angle)
        z = data[2] * math.cos(angle) - data[0] * math.sin(angle)
        data[0] = x
        data[2] = z
    return(list)

"calculate scaled XYZ values based on scalar and user picked landmarks. this probably should go in the 'scale' function"
def scaleXYZ(scalar, xyz):
    new_xyz = np.multiply(xyz, scalar)
    return (new_xyz)

"CALCULATE DISTANCE BETWEEN NASEON AND BASEON  and scale everything based on that distance"
def scale(data, basion, nasion):
    distance = math.sqrt((basion[0]-nasion[0])**2 + (basion[1] - nasion[1])**2 + (basion[2] - nasion [2])**2 )
    distance = abs(distance)
    scalar = 10000/distance
    print('the scalar is ' + str(scalar))
    scaled = np.multiply(data, scalar)
    return(scaled, scalar)

"initial write excel spreadsheet of rounded xyz and theta phi values - not sure best way to store data. Need alkureishi and server guy input"
def writeExcel(toWrite, name):
    short_name = name[:-4]
    df = pd.DataFrame(toWrite)
    df.rename(columns={0: 'X', 1: 'Y' , 2: 'Z' , 3: 'Radius from Sella', 4: 'Theta from Sella',5:'Phi From Sella'}, inplace=True)
    writer = pd.ExcelWriter('EXCEL_RESULT_'+short_name+'.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Result', index=False)
    writer.save()

"round radius, theta, and phi values to some significant digits"
def forceSigFigs(data,x, y, z):
    for value in data:
        value[3] = np.format_float_positional(value[3], precision = x, unique = False)
        value[4] = np.format_float_positional(value[4], precision = y, unique = False)
        value[5] = np.format_float_positional(value[5], precision = z, unique = False)
    return(data)

"write PLY files from final data might be good idea to try and store oriented normals if attempting stl conversion within code"
def writePLY(xyz, name):
    print('Generating final point cloud and stl file for your convenience... Hang tight!')
    pcd = o3d.geometry.PointCloud()
    print(xyz)
    pcd.points = o3d.utility.Vector3dVector(xyz)
    # pcd.estimate_normals()
    # pcd.orient_normals_consistent_tangent_plane(10)
    o3d.visualization.draw_geometries([pcd])
    ply_file = "./"+name+".ply"
    o3d.io.write_point_cloud(name, pcd)
    
"get rid of nonfloat data points in the final data set"
def cleanUpData(data):
    cleaned = []
    for value in data:
        if isinstance(value[2], float) and isinstance(value[3], float) == True:
            cleaned.append(value)
    return (cleaned)        
            
"retain phi values that are on the user designated  angular interval"
def sortByPhi(n, values):
    sorted = []
    for item in values:
        result = Decimal(str(item[5])) % Decimal(str(n))
        #result_round = round(result, 1)
        if result == 0:
            sorted.append(item)   
    return(sorted)

"retain theta values that are on the user designated angular interval"
def sortByTheta(n, values):
    sorted = []
    for item in values:
        result = Decimal(str(item[4])) % Decimal(str(n))
        #result_round = round(result, 1)
        if result == 0:
            sorted.append(item)   
    return(sorted) 
  
"function that does the actual averaging. Extremely inefficient due to nested loops and should probably be improved eventually"
def compare(big_list):
    zz = 1 
    max_lists_init = []
    "max lists contains the maximum radius xyz coords for each unique theta phi pair"
    for subset in big_list:
        print('Entering Analysis Portion')
        print('number of skulls = '  + str(len(big_list)))
        print('List of skull ' + str(zz) + ' is ' + str(len(subset)) + ' points long.')
        print('Starting analysis of skull ' + str(zz))
        zz+=1
        data_to_store = []
        start_single_skull = time.time()
        for thing in subset:
            temp_list01 = []
            for item in subset:
                if item[4] == thing[4] and item[5] == thing[5]:
                    temp_list01.append(item)
            radius_list = []
            for point in temp_list01:
                radius_list.append(point[3])
            index = radius_list.index(max(radius_list))
            data_to_store.append(temp_list01[index])
        max_lists_init.append(data_to_store) 
        end_single_skull = time.time()
        print(f'This skull took {(end_single_skull - start_single_skull)} seconds')
        
    "get rid of duplicate values in lists to save time in averaging steps. probably better way to do this."
    max_lists = [[],[]]  
    [max_lists[0].append(x) for x in max_lists_init[0] if x not in max_lists[0]]
    [max_lists[1].append(x) for x in max_lists_init[1] if x not in max_lists[1]]

    #make average xyz based on max radius. use these to iterate
    running_average = []
    #take last list of this list and do averages.... 
    print('Starting averaging process')
    max_lists.sort(reverse=True, key = len)
    largest_list = max_lists[0]
    max_lists.pop(0)
    start_single_skull = time.time()
    for data in largest_list:
        for value in max_lists[0]:
            if data[4] == value[4] and data[5] == value[5]:
                temp = []
                average_x = (data[0] + value[0]) / 2
                average_y = (data[1] + value[1]) / 2
                average_z = (data[2] + value[2]) / 2
                temp.append(average_x)
                temp.append(average_y)
                temp.append(average_z)
                temp.append(data[3])
                temp.append(data[4])
                temp.append(data[5])
                running_average.append(temp)           
    end_single_skull = time.time()
    print(f'Averaging took {(end_single_skull - start_single_skull)} seconds')
    "get rid of duplicate values in running average list. not sure if need to do this because happens earlier in function but kept in bc low time cost."
    running_average_return = []  
    [running_average_return.append(x) for x in running_average if x not in running_average_return]
    # make array of running average return for plotting and saving
    average_arr = np.array(running_average_return)
    average_xyz = average_arr[:,:3]
    # open3DPick(average_xyz)
    return average_xyz,running_average_return

##### SELECT FILES AND DO FILE CONVERSION #####
file_input = fileSelect()
name_list = [item[item.rindex('/')+1:] for item in file_input]       
print(name_list)
# print(name_list)
big_list = []
######## SET ANGLE INTERVAL #######
theta_int = args.theta
phi_int = args.phi

"loop count only here for testing"
loop_count = 0
"main loop of progran"
for file in name_list:
    points_array, points_list = convertFile(file, density)
    "Un highlight these for real tests. An error gets thrown later on and need to add index 0 to some variables when unsuspended"
    R_porion_index = getData('RIGHT PORION', points_array)
    L_porion_index = getData('LEFT PORION', points_array)
    naseon_index = getData('NASEON', points_array)
    basion_index = getData('BASION', points_array)
    
    right_porion_xyz = points_array[R_porion_index[0]]
    left_porion_xyz = points_array[L_porion_index[0]]
    naseon_xyz = points_array[naseon_index[0]]
    basion_xyz = points_array[basion_index[0]]

    "testing loops when 'DGF....ply' and 'RXU....ply' and 'PXI....ply' are selected in that order"
    #DGF
    # if loop_count == 0: 
    #     right_porion_xyz = points_array[127657]
    #     left_porion_xyz = points_array[190837]
    #     L_porion_index = 190837
    #     basion_xyz = points_array[100412]
    #     naseon_xyz = points_array[274158]
    #     naseon_index = 274158
    # # #RXU
    # if loop_count == 1:
    #     right_porion_xyz = points_array[120067]
    #     left_porion_xyz = points_array[133376]
    #     L_porion_index = 133376
    #     basion_xyz = points_array[53064]
    #     naseon_xyz = points_array[227764]
    #     naseon_index = 227764
    # #PXI 
    # if loop_count == 2:
    #     right_porion_xyz = points_array[107382]
    #     left_porion_xyz = points_array[181165]
    #     L_porion_index = 181165
    #     basion_xyz = points_array[90989]
    #     naseon_xyz = points_array[167390]
    #     naseon_index = 167390

    " SCale data to 10000/ distance between nasion and basion "
    scaled, scalar = scale(points_list, basion_xyz, naseon_xyz)
    scaled_right_porion_xyz = scaleXYZ(scalar, right_porion_xyz)
    scaled_left_porion_xyz = scaleXYZ(scalar,left_porion_xyz)
    scaled_naseon_xyz = scaleXYZ(scalar,naseon_xyz)
    scaled_BASION_xyz = scaleXYZ(scalar, basion_xyz)
    

    "TRANSFORM DATA SET TO PUT *BASION* AT ORIGIN: REPOSITION SKULL STEP 1"
    basion_transform = scaled - scaled_BASION_xyz 

    "ROTATE ALL VALUES TO PUT RIGHT PORION ON POSITIVE X AXIS "
    "transform right poreon point"
    r_poreon_transform = scaled_BASION_xyz - scaled_right_porion_xyz
    "get angle to do rotation and then rotate"
    poreon_angle = getAngle_Z(r_poreon_transform)
    poreon_trans_rotate = fixPoreon(basion_transform, poreon_angle)
    "ROTATE ALL VALUES TO PUT NASEON ON POSITIVE Y AXIS "
    naseon_transform_xyz = scaled_naseon_xyz-scaled_BASION_xyz
    "get rotated naseon xyz"
    naseon_rotate_xyz = poreon_trans_rotate[naseon_index] 
    "get angle with which to rotate data set to position of naseon and then rotate"
    nason_angle = getAngle_X(naseon_rotate_xyz)
    naseon_trans_rotate = fixNaseon(poreon_trans_rotate, nason_angle)

    "ROTATE ALL VALUES TO PUT L POREON ON POSITIVE Y AXIS "
    L_porion_transform_xyz = scaled_left_porion_xyz - scaled_BASION_xyz
    "get rotated poreon xyz"
    L_poreon_rotate_2x = naseon_trans_rotate[L_porion_index]
    L_poreon_angle = getAngle_Y(L_poreon_rotate_2x)
    data_final = fixBasion(naseon_trans_rotate, L_poreon_angle)
   
    " BEGIN FINAL MATH AND SORTING STEPS "
    data_final_list = data_final.tolist()
    result = doMath(data_final_list)
    "convert to array to do rouding before converting back to list. should probably be improved"
    result_array = np.array(result)
    abridged_array = forceSigFigs(result_array, 9, sig_phi, sig_theta)
    abridged_list = abridged_array.tolist()

    "gets rid of non floats- not sure if this is neccesary but keeping just in case"
    cleanData = cleanUpData(abridged_list)

    "keep data only with proper theta and phi values. Could maybe wrap into one function"
    phi_edited = sortByPhi(float(phi_int),cleanData)
    final_list = sortByTheta(float(theta_int), phi_edited)
    tempArray = np.array(final_list)
    final_array_xyz = tempArray[:,:3]
    
    "only here for testing"
    # if loop_count == 0:
    #     writePLY(final_array_xyz, './in_1.ply')
    # if loop_count == 1:
    #     writePLY(final_array_xyz, './in_2.ply')
    # if loop_count == 2:
    #     writePLY(final_array_xyz, './in_3.ply')  
    # open3DPick(final_array_xyz)
    
    print('length of skull xyz points list is ' + str(len(final_list)))
    "only use when writing data and if interested in seeing sliced model"
    # writeExcel(theta_edited,names[loop_count])
    # open3DPick(final_array_xyz)
    
    big_list.append(final_list)
    loop_count+=1



"""
Following loops send parsed data to compare function to generate nornative model. idea is that
if multiple skulls as input, we can create a running average of them and feed the running average 
back to the function with the next input. Doing it by len of list is ugly, but seems to work for now.
This is the big update from 12/02/23 and significantly improved the output of multiple skulls as well 
as the time (althogh it is still very slow at theta/ phi <3) (see figure 5A)
"""
if len(big_list) == 2:
    data_array, running_average_list = compare(big_list)
    print(data_array)
    writePLY(data_array, './2_ave_TEST.ply')
    open3DPick(data_array)
    """
    dont need these unless trying to generate ply file with inputs as well as average.
    Couldnt figure out how to color code individual points easily, however, so gave up
    """
    # pcd1 = np.array(big_list[0])
    # pcd1 = pcd1[:,:3]
    # pcd2 = np.array(big_list[1])
    # pcd2 = pcd2[:,:3]
    # master = []
    # for item in data_array:
    #     master.append(item)
    # for item in pcd1:
    #     master.append(item)
    # for item in pcd2:
    #     master.append(item)
    # master=np.array(master)
    # open3DPick(master)


elif len(big_list) == 3:
    second_round = big_list[-1]
    data_array, running_average_list = compare(big_list[0:2])
    big_list_1 = []
    big_list_1.append(running_average_list)
    big_list_1.append(second_round)
    data_array1, running_average_list1 = compare(big_list_1)
    # writePLY(data_array1, './3_ave_.ply')
    # open3DPick(data_array1)
    # pcd1 = np.array(big_list[0])
    # pcd1 = pcd1[:,:3]
    # pcd2 = np.array(big_list[1])
    # pcd2 = pcd2[:,:3]
    # pcd3 = np.array(big_list[2])
    # pcd3 = pcd3[:,:3]
    # master = []
    # for item in data_array:
    #     master.append(item)
    # for item in pcd1:
    #     master.append(item)
    # for item in pcd2:
    #     master.append(item)       

elif len(big_list == 4):
    second_round = big_list[-1]
    third_round = big_list[-2]
    data_array, running_average_list = compare(big_list[0:2])
    running_average_list.append(second_round)
    data_array1, running_average_list1 = compare(running_average_list)
    running_average_list1.append(third_round)
    data_array2, running_average_list2 = compare(running_average_list1)
    writePLY(data_array2, '0930t5p5result')
    print(data_array2)
    # open3DPick(data_array2)



finish = time.time()


time_tot = finish-start
print(time_tot)











