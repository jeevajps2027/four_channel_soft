from django.shortcuts import render


def parameter(request):
    return render(request,"app/parameter.html")