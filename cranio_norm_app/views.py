from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from .forms import HomeForm


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
                return HttpResponseRedirect('/thanks/')
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()

    return render(request, 'home.html', {'form': form})

