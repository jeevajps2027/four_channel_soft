
import os
from django.http import JsonResponse
from django.shortcuts import redirect, render
import json
from django.views.decorators.csrf import csrf_exempt
from app.models import paraTableData,Parameter_Settings

@csrf_exempt  # Add CSRF exemption only if not handling with CSRF token
def measurement(request):
    if request.method == 'GET':
        part_model = list(Parameter_Settings.objects.order_by('id').values_list('part_model', flat=True).distinct())           
        print('Your part names from database:', part_model)

        context = {
            'part_model':part_model,
            
        }

    return render(request, 'app/measurement.html', context)
