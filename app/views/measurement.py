from django.http import JsonResponse
from django.shortcuts import redirect, render
import json
from django.views.decorators.csrf import csrf_exempt
from app.models import Data_Shift, User_Data, master_data, paraTableData, Parameter_Settings


@csrf_exempt
def measurement(request):
    if request.method == 'POST':
        
        part_model_get = request.POST.get('part_model', '')
        print("part_model_get:", part_model_get)

        parameter_settings = Parameter_Settings.objects.filter(part_model=part_model_get).first()

        part_name_value = parameter_settings.part_name
        char_lock_value = parameter_settings.char_lock
        char_lock_limit_value = parameter_settings.char_lock_limit
        punch_no_value = parameter_settings.punch_no


       

        related_data = paraTableData.objects.filter(parameter_settings__part_model=part_model_get).select_related('parameter_settings').order_by('id')

        
        # Extract and prepare data for response
        parameter_name_array = []
        channel_no_array = []
        low_master_array = []
        high_master_array = []
        nominal_array = []
        lsl_array = []
        usl_array = []
        ltl_array = []
        utl_array = []
        step_no_array = []
        auto_man_array = []
        timer_array = []
        digits_array = []

        for data in related_data:
            parameter_name_array.append(data.parameter_name)
            channel_no_array.append(data.channel_no)
            low_master_array.append(data.low_master)
            high_master_array.append(data.high_master)
            nominal_array.append(data.nominal)
            lsl_array.append(data.lsl)
            usl_array.append(data.usl)
            ltl_array.append(data.ltl)
            utl_array.append(data.utl)
            step_no_array.append(data.step_no)
            auto_man_array.append(data.auto_man)
            timer_array.append(data.timer)
            digits_array.append(data.digits)


        filtered_data = Parameter_Settings.objects.filter(
            part_model=part_model_get
        ).order_by('id')  # Ensures the order is by 'id'

        print('Filtered data from Parameter_Settings:', filtered_data)

        # Step 2: Get all `parameter_name` values from `paraTableData` related to `filtered_data`
        parameter_names = paraTableData.objects.filter(
            parameter_settings__in=filtered_data
        ).values_list('parameter_name', flat=True).distinct().order_by('parameter_settings__id')

        print('Parameter names from paraTableData:', list(parameter_names))

        last_stored_parameters = {
            item['parameter_name']: item
            for item in master_data.objects.filter(
                part_model=part_model_get,
                parameter_name__in = parameter_names.values_list('parameter_name', flat=True)
                  # Ensure it matches the selected_value context
            ).values().order_by('parameter_name')  # Fetch all fields
        }

        # Step 4: Print the required fields (id, e, d, o1) for each parameter_name
        for param_name, values in last_stored_parameters.items():
            id = values.get('id')
            e = values.get('e')
            d = values.get('d')
            o1 = values.get('o1')
            print(f"Parameter: {param_name}, id: {id}, e: {e}, d: {d}, o1: {o1}")

        parameter_values = [
            {
                "parameter_name": param_name,
                "id": values.get("id"),
                "e": values.get("e"),
                "d": values.get("d"),
                "o1": values.get("o1")
            }
            for param_name, values in last_stored_parameters.items()
        ]   

        # Sending data in JSON format
        return JsonResponse({
            'part_name_value':part_name_value,
            'char_lock_value':char_lock_value,
            'char_lock_limit_value':char_lock_limit_value,
            'punch_no_value':punch_no_value,
            'parameter_name_array': parameter_name_array,
            'channel_no_array': channel_no_array,
            'low_master_array': low_master_array,
            'high_master_array': high_master_array,
            'nominal_array': nominal_array,
            'lsl_array': lsl_array,
            'usl_array': usl_array,
            'ltl_array': ltl_array,
            'utl_array': utl_array,
            'step_no_array': step_no_array,
            'auto_man_array': auto_man_array,
            'timer_array': timer_array,
            'digits_array': digits_array,
            'parameter_values':parameter_values,
        })
    

    elif request.method == 'GET':

        # Fetch distinct part_model values
        part_model = list(Parameter_Settings.objects.order_by('id').values_list('part_model', flat=True).distinct())           
        print('Your part names from database:', part_model)

        user_name=list(User_Data.objects.all().values())
        shift_time=list(Data_Shift.objects.all().order_by('id').values())
        print("shift_time",shift_time)

        context = {
            'part_model': part_model,
            'user_name':json.dumps(user_name),
             'shift_time':json.dumps(shift_time)

        }

    return render(request, 'app/measurement.html', context)
