from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'index.html', {})

def profile(request):
    return render(request, 'profile.html', {})

def garage(request):
    return render(request, 'garage.html', {})

def map(request):
    return render(request, 'map.html', {})

def motodetails(request, moto_id):
    return render(request, 'motodetails.html', {})

def motoadd(request):
    return render(request, 'motoadd.html', {})