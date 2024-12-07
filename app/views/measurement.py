from django.shortcuts import render


def measurement(request):
    return render(request,"app/measurement.html")