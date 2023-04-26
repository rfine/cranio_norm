from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from .forms import HomeForm
from .file_service import FileService
import json
from .constants import *
import numpy as np
import math
import aspose.threed as a3d
import time 
from plyfile import PlyData
from decimal import Decimal


from datetime import datetime

import open3d as o3d
import pandas as pd


def home(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = HomeForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
    
        # check whether it's valid:
        if form.is_valid():
            if len(files) < 2:
                form.add_error('files',ValidationError("More than one file needs to be selected"))
                return render(request, 'home.html', {'form': form})
            else:
                data = []
                for file in files:
                    file_service = FileService(file)
                    file_name = file_service.convertSTLToPLY()
                    data.append(file_name)
                    # redirect with session
                start_time = time.time()
                request.session['ply_file_names'] = data
                request.session['phi'] =  form.cleaned_data.get("phi")
                request.session['theta'] =  form.cleaned_data.get("theta")
                request.session['phi_sig'] =  form.cleaned_data.get("phi_sig")
                request.session['theta_sig'] =  form.cleaned_data.get("theta_sig")

                print("--- %s create session ---" % (time.time() - start_time))
                return redirect('skull_input')
            

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()

    return render(request, 'home.html', {'form': form})

def skull_input(request):
    start_time = time.time()
    json_obj = json.dumps(request.session['ply_file_names'])
    print("--- %s skull_input ---" % (time.time() - start_time))
    return render(request, 'skull_input.html', {'data': json_obj})




def getAngle_X(xyz_list):
    # get angle to rotate whole skull from the naseon now
    # print(xyz_list)
    angle_naseon = math.atan(xyz_list[2]/xyz_list[1])  # is in radians
    #NEED TO IMPLEMENT A CHECKPOINT HERE TO MAKE SURE THAT THIS WORKS EVERY TIME #
    rot_angle_naseon = (-1*angle_naseon)
    return(rot_angle_naseon)


def fixNaseon(trans_rotate_list, angle):
    for data in trans_rotate_list:
        y = data[1] * math.cos(angle) - data[2] * math.sin(angle)
        z = math.sin(angle) * data[1] + data[2] * math.cos(angle)
        data[1] = y
        data[2] = z
    return(trans_rotate_list)


def scale(data, basion, nasion):
    reduce_data = [item[:3] for item in data]
    distance = math.sqrt(
        (basion[0]-nasion[0])**2 + (basion[1] - nasion[1])**2 + (basion[2] - nasion[2])**2)
    distance = abs(distance)
    scalar = 10000/distance
    scaled = np.multiply(reduce_data, scalar)
    
    return(scaled, scalar)

# TODO why do we need this? we already scale the entire dataset 
def scaleXYZ(scalar, xyz):
    new_xyz = np.multiply(xyz, scalar)
    return (new_xyz)


def getAngle_Z(xyz_list):
    # get rotation angle using tan inverse of y/x
    angle = math.atan(xyz_list[1]/xyz_list[0])  # is in radians
    rot_angle = (math.pi - angle)
    return (rot_angle)


def fixPoreon(transformList, angle):
    # Solve for new x and y values for all values
    for data in transformList:
        x = math.cos(angle) * data[0] - data[1] * math.sin(angle)
        y = data[1] * math.cos(angle) + data[0] * math.sin(angle)
        data[0] = x
        data[1] = y
    return(transformList)

def getAngle_Y(xyz_list):
    # get angle to rotate whole skull from the naseon now
    angle_naseon = math.atan(xyz_list[2]/xyz_list[0])  # is in radians
    rot_angle_naseon = (-1*angle_naseon)
    return(rot_angle_naseon)

def fixBasion(list, angle):
    # Solve for new values using that angle and system of equations
    for data in list:
        x = data[2] * math.sin(angle) + data[0] * math.cos(angle)
        z = data[2] * math.cos(angle) - data[0] * math.sin(angle)
        data[0] = x
        data[2] = z
    return(list)


def doMath(list_of_coords):
    returnList = []
    for coord in list_of_coords:
        temp = []
        temp.append(coord[0])
        temp.append(coord[1])
        temp.append(coord[2])
        radius1 = math.sqrt(coord[0]**2 + coord[1]**2 + coord[2]**2)
        phi_rad = math.atan2(coord[1], coord[0])
        theta_rad = math.acos(coord[2]/radius1)
        phi_deg = math.degrees(phi_rad)
        theta_deg = math.degrees((theta_rad))
        temp.append(radius1)
        temp.append(theta_deg)
        temp.append(phi_deg)
        returnList.append(temp)
    return (returnList)

# TODO why do we really care about this. Very long runtime
def forceSigFigs(data, x, y, z):
    for value in data:
        value[3] = np.format_float_positional(
            value[3], precision=x, unique=False)
        value[4] = np.format_float_positional(
            value[4], precision=y, unique=False)
        value[5] = np.format_float_positional(
            value[5], precision=z, unique=False)
    return(data)

def sortByPhi(n, values):
    sorted = []
    for item in values:
        result = Decimal(str(item[5])) % Decimal(str(n))
        #result_round = round(result, 1)
        if result == 0:
            sorted.append(item)
    return(sorted)


def divisionPhi(n, d):
    return math.atan(n/d)if d else 0


def divisionTheta(n, d):
    return math.acos(n / d)if d else 0

"retain theta values that are on the user designated angular interval"


def sortByTheta(n, values):
    sorted = []
    for item in values:
        result = Decimal(str(item[4])) % Decimal(str(n))
        #result_round = round(result, 1)
        if result == 0:
            sorted.append(item)
    return(sorted)


def cleanUpData(data):
    cleaned = []
    for value in data:
        if isinstance(value[2], float) and isinstance(value[3], float) == True:
            cleaned.append(value)
    return (cleaned)


def compare(big_list):
    zz = 1
    check_list = []
    "max lists contains the maximum radius xyz coords for each unique theta phi pair"
    for subset in big_list:
        df =  pd.DataFrame(subset, columns=['x','y','z','radius','phi','theta'])
        print('Entering Analysis Portion')
        print('number of skulls = ' + str(len(big_list)))
        print('List of skull ' + str(zz) + ' is ' +
              str(len(subset)) + ' points long.')
        print('Starting analysis of skull ' + str(zz))
        zz += 1
        start_single_skull = time.time()

        idx = df.groupby(['phi', 'theta'])['radius'].transform(max) == df['radius']
        result_df = df[idx]
        result_list = result_df.values.tolist()
        check_list.append(result_list)
        end_single_skull = time.time()
        print(
            f'This skull took {(end_single_skull - start_single_skull)} seconds')

    "get rid of duplicate values in lists to save time in averaging steps. probably better way to do this."
    max_lists = [[], []]
    [max_lists[0].append(x)
     for x in check_list[0] if x not in max_lists[0]]
    [max_lists[1].append(x)
     for x in check_list[1] if x not in max_lists[1]]

    # make average xyz based on max radius. use these to iterate
    running_average = []
    # take last list of this list and do averages....
    print('Starting averaging process')
    max_lists.sort(reverse=True, key=len)
    largest_list = max_lists[0]
    max_lists.pop(0)
    start_single_skull = time.time()
    #  TODO update and optimize 
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
    [running_average_return.append(
        x) for x in running_average if x not in running_average_return]
    # make array of running average return for plotting and saving
    average_arr = np.array(running_average_return)
    average_xyz = average_arr[:, :3]
    # open3DPick(average_xyz)
    return average_xyz, running_average_return


def writePLY(xyz):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    pcd.estimate_normals()
    # o3d.visualization.draw_geometries([pcd])
    now = datetime.now()
    ply_name = "output"
    ply_path = "./cranio_norm_app/static/ply/"+ply_name+".ply"
    o3d.io.write_point_cloud(ply_path, pcd, write_ascii=True)
    return ply_name



# TODO get the data directly with the index with PLYDATA
def points(request):
    skull_list = json.loads(request.POST.get('index'))
    file_names = request.session['ply_file_names']

    phi = request.session['phi'] 
    theta = request.session['theta'] 
    phi_sig = request.session['phi_sig'] 
    theta_sig = request.session['theta_sig'] 


    big_list = [] 
    for index, file_name in enumerate(file_names):
        # open 
        plydata = PlyData.read("./cranio_norm_app/static/ply/"+file_name)
        points_list = plydata["vertex"].data.tolist()


        right_porion_xyz = points_list[skull_list[index][RIGHT_PORION]][:3]
        left_porion_xyz = points_list[skull_list[index][LEFT_PORION]][:3]
        naseon_xyz = points_list[skull_list[index][NASEON]][:3]
        basion_xyz = points_list[skull_list[index][BASION]][:3]


        # right_porion_xyz = np.asarray(plydata["vertex"].data[skull_list[index][RIGHT_PORION]]).tolist()[:3]
        # left_porion_xyz = np.asarray(plydata["vertex"].data[skull_list[index][LEFT_PORION]]).tolist()[:3]
        # naseon_xyz = np.asarray(plydata["vertex"].data[skull_list[index][NASEON]]).tolist()[:3]
        # basion_xyz = np.asarray(plydata["vertex"].data[skull_list[index][BASION]]).tolist()[:3]

        scaled, scalar = scale(points_list, basion_xyz, naseon_xyz)
        # TODO should just be able to access it from the scaled var no need for a function
        scaled_right_porion_xyz = scaleXYZ(scalar, right_porion_xyz)
        scaled_left_porion_xyz = scaleXYZ(scalar, left_porion_xyz)
        scaled_naseon_xyz = scaleXYZ(scalar, naseon_xyz)
        scaled_BASION_xyz = scaleXYZ(scalar, basion_xyz)


        # TRANSFORM DATA SET TO PUT *BASION* AT ORIGIN: REPOSITION SKULL STEP 1
        # TODO make scaled only 3 variable *************
        basion_transform = scaled - scaled_BASION_xyz
        # "ROTATE ALL VALUES TO PUT RIGHT PORION ON POSITIVE X AXIS "
        # "transform right poreon point"
        r_poreon_transform = scaled_BASION_xyz - scaled_right_porion_xyz
        # "get angle to do rotation and then rotate"
        poreon_angle = getAngle_Z(r_poreon_transform)
        poreon_trans_rotate = fixPoreon(basion_transform, poreon_angle)
        # "ROTATE ALL VALUES TO PUT NASEON ON POSITIVE Y AXIS "
        naseon_transform_xyz = scaled_naseon_xyz-scaled_BASION_xyz
        # "get rotated naseon xyz"
        naseon_rotate_xyz = poreon_trans_rotate[skull_list[index][NASEON]]


        nason_angle = getAngle_X(naseon_rotate_xyz)
        naseon_trans_rotate = fixNaseon(poreon_trans_rotate, nason_angle)

        "ROTATE ALL VALUES TO PUT L POREON ON POSITIVE Y AXIS "
        L_porion_transform_xyz = scaled_left_porion_xyz - scaled_BASION_xyz
        "get rotated poreon xyz"
        L_poreon_rotate_2x = naseon_trans_rotate[skull_list[index][LEFT_PORION]]
        L_poreon_angle = getAngle_Y(L_poreon_rotate_2x)
        data_final = fixBasion(naseon_trans_rotate, L_poreon_angle)


        " BEGIN FINAL MATH AND SORTING STEPS "
        data_final_list = data_final.tolist()
        result = doMath(data_final_list)
        "convert to array to do rouding before converting back to list. should probably be improved"
        result_array = np.array(result)
        abridged_array = forceSigFigs(result_array, 9, phi_sig, theta_sig)
        abridged_list = abridged_array.tolist()

        "gets rid of non floats- not sure if this is neccesary but keeping just in case"
        # TODO should not need it 
        cleanData = cleanUpData(abridged_list)

        "keep data only with proper theta and phi values. Could maybe wrap into one function"
        phi_edited = sortByPhi(float(phi), cleanData)
        final_list = sortByTheta(float(theta), phi_edited)
        # tempArray = np.array(final_list)
        # final_array_xyz = tempArray[:, :3]


        print('length of skull xyz points list is ' + str(len(final_list)))
        "only use when writing data and if interested in seeing sliced model"

        big_list.append(final_list)

    if len(big_list) == 2:
        data_array, running_average_list = compare(big_list)

        # create filename output_dt
        # write ply file to certain location 
        # redirect to output page 

        file_name = writePLY(data_array)
        return render(request, 'output.html', {'data': json.dumps(file_name)})
        
    