from django.shortcuts import render


def gen_setting(request):
    return render(request,"app/gen_setting.html")