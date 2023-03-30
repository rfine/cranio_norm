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
                    point_cloud_array, point_cloud_list = file_service.convertFile()
                    data.append(point_cloud_list)
                    # redirect with session
                request.session['point_cloud_list'] = data
                return redirect('skull_input')
            

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()

    return render(request, 'home.html', {'form': form})

def skull_input(request):
    json_obj = request.session['point_cloud_list']
    return render(request, 'skull_input.html', {'data': json_obj})




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


def points(request):
    skull_list = json.loads(request.POST.get('index'))
    point_cloud_list = request.session['point_cloud_list']
    for index, skull in enumerate(skull_list):

        print(point_cloud_list[index][skull[RIGHT_PORION]])
        right_porion_xyz = point_cloud_list[index][skull[RIGHT_PORION]]
        left_porion_xyz = point_cloud_list[index][skull[LEFT_PORION]]
        naseon_xyz = point_cloud_list[index][skull[NASEON]]
        basion_xyz = point_cloud_list[index][skull[BASION]]
    