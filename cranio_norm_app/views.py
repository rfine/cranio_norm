from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from .forms import HomeForm
from .file_service import FileService
import json

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
                # need to process for all files before redirecting... 
                data = []
                for file in files:
                    file_service = FileService(file)
                    point_cloud_array, point_cloud_list = file_service.convertFile()
                    data.append(point_cloud_list)
                    # redirect with session
                request.session['data'] = data
                return redirect('skull_input')
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()

    return render(request, 'home.html', {'form': form})

def skull_input(request):
    json_obj = request.session['data']
    return render(request, 'skull_input.html', {'data': json_obj})