from django.shortcuts import render


def report(request):
    return render(request,'app/report.html')