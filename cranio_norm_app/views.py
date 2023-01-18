from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request,'home.html')


def file_upload(request):
    for f in request.FILES.getlist('file-input'):
        file = f
