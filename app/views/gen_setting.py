import json
from django.http import JsonResponse
from django.shortcuts import render
from app.models import Operator_setting  # Import your model

def gen_setting(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            
            # Process and save each entry in the database
            for row in data:
                operator_no = row.get("operator_no")
                operator_name = row.get("operator_name")
                
                if operator_no and operator_name:
                    # Create or update the operator setting
                    # Assuming operator_no is unique, you can use `get_or_create` to handle duplicates
                    operator, created = Operator_setting.objects.get_or_create(
                        operator_no=operator_no,
                        defaults={'operator_name': operator_name}
                    )
                    if not created:
                        # If the record exists, update the operator_name
                        operator.operator_name = operator_name
                        operator.save()

                    print(f"Operator No: {operator_no}, Operator Name: {operator_name}")
                else:
                    return JsonResponse({"status": "error", "message": "Missing operator_no or operator_name"})
            
            return JsonResponse({"status": "success", "message": "Data saved successfully"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        
    elif request.method == "GET":
        operators_value = Operator_setting.objects.all().order_by('id')
        context={
            "operators_value":operators_value,
        }
    
    return render(request, "app/gen_setting.html",context)
