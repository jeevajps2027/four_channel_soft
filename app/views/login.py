from django.http import JsonResponse
from django.shortcuts import render
from app.models import Operator_setting
import json

def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Check credentials
            if username == 'saadmin' and password == 'saadmin':
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'redirect': '/measurement/'})
            
            # Check against Operator_setting
            elif Operator_setting.objects.filter(operator_name=username).exists() and password == 'admin@123':
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'redirect': '/measurement/'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
    elif request.method == 'GET':
        operators = Operator_setting.objects.all()
        operator_names = [operator.operator_name for operator in operators]
        return render(request, 'app/login.html', {'operator_names': operator_names})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)