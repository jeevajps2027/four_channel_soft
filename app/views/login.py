from django.http import JsonResponse
from django.shortcuts import render
from app.models import Operator_setting, User_Data
import json

def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username:
                return JsonResponse({'status': 'error', 'message': 'Username is required.'}, status=400)

            user, created = User_Data.objects.get_or_create(id=1)  # Always use ID 1
            user.username = username  # Update the username field with the new value
            user.save()

            # Print information about the operation
            if created:
                print(f'New username created: {user.username}')
            else:
                print(f'Username already exists: {user.username}')

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