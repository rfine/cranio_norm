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
                # TODO remove the need to instantiate an empty data 
                data = []
                for file in files:
                    file_service = FileService(file)
                    point_cloud_array, point_cloud_list = file_service.convertFile()
                    data.append(point_cloud_list)
                    # redirect with session
                request.session['point_cloud_list'] = data
                return redirect('skull_input')
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()

    return render(request, 'home.html', {'form': form})

def skull_input(request):
    json_obj = request.session['point_cloud_list']
    return render(request, 'skull_input.html', {'data': json_obj})

# # TODO refactor into seperate service class
# def scale(data, basion, nasion):
#     distance = math.sqrt(
#         (basion[0]-nasion[0])**2 + (basion[1] - nasion[1])**2 + (basion[2] - nasion[2])**2)
#     distance = abs(distance)
#     scalar = 10000/distance
#     print('the scalar is ' + str(scalar))
#     print(type(data))
#     scaled = np.multiply(data, scalar)
#     return(scaled, scalar)

# def scaleXYZ(scalar, xyz):
#     new_xyz = np.multiply(xyz, scalar)
#     return (new_xyz)

# def getAngle_Z(xyz_list):
#     # get rotation angle using tan inverse of y/x
#     angle = math.atan(xyz_list[1]/xyz_list[0])  # is in radians
#     rot_angle = (math.pi - angle)
#     return (rot_angle)

# def fixPoreon(transformList, angle):
#     # Solve for new x and y values for all values
#     for data in transformList:
#         x = math.cos(angle) * data[0] - data[1] * math.sin(angle)
#         y = data[1] * math.cos(angle) + data[0] * math.sin(angle)
#         data[0] = x
#         data[1] = y
#     return(transformList)


def getAngle_X(xyz_list):
    # get angle to rotate whole skull from the naseon now
    # print(xyz_list)
    angle_naseon = math.atan(xyz_list[0][2]/xyz_list[0][1])  # is in radians
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

# TODO create a find index function or see if there is a way in the frontend to do this
#  just need to bring back the indices 
def points(request):
    # request.POST.get('my_field')
    skull_list = json.loads(request.POST.get('index'))
    point_cloud_list = request.session['point_cloud_list']
    for index, skull in enumerate(skull_list):

        print(point_cloud_list[index][skull[RIGHT_PORION]])
        right_porion_xyz = point_cloud_list[index][skull[RIGHT_PORION]]
        left_porion_xyz = point_cloud_list[index][skull[LEFT_PORION]]
        naseon_xyz = point_cloud_list[index][skull[NASEON]]
        basion_xyz = point_cloud_list[index][skull[BASION]]

        # scaled, scalar = scale(point_cloud_list[index], basion_xyz, naseon_xyz)
        # scaled_right_porion_xyz = scaleXYZ(scalar, right_porion_xyz)
        # scaled_left_porion_xyz = scaleXYZ(scalar, left_porion_xyz)
        # scaled_naseon_xyz = scaleXYZ(scalar, naseon_xyz)
        # scaled_BASION_xyz = scaleXYZ(scalar, basion_xyz)

        # basion_transform = scaled - scaled_BASION_xyz
        # r_poreon_transform = scaled_BASION_xyz - scaled_right_porion_xyz
        # poreon_angle = getAngle_Z(r_poreon_transform)
        # poreon_trans_rotate = fixPoreon(basion_transform, poreon_angle)

        # naseon_transform_xyz = scaled_naseon_xyz-scaled_BASION_xyz
        # # why do we have index here? wouldnt this just be a single point?
        # naseon_rotate_xyz = poreon_trans_rotate[naseon_index]

        # nason_angle = getAngle_X(naseon_rotate_xyz)
        # naseon_trans_rotate = fixNaseon(poreon_trans_rotate, nason_angle)

        # L_porion_transform_xyz = scaled_left_porion_xyz - scaled_BASION_xyz

        # L_poreon_rotate_2x = naseon_trans_rotate[L_porion_index]

    