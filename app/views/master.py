from django.shortcuts import render


def master(request):
    return render(request,"app/master.html")