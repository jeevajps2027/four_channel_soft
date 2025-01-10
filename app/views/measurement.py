from datetime import datetime
import os
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from app.models import MeasurementData, Parameter_Settings,part_retrived, ComportSetting, Data_Shift,User_Data, master_data, paraTableData
import serial.tools.list_ports
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncDate


def get_available_com_ports():
    return [port.device for port in serial.tools.list_ports.comports()]


@csrf_exempt  # Add CSRF exemption only if not handling with CSRF token
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
        ports_string = ''
        comport_com_port = ComportSetting.objects.values_list('com_port', flat=True).first()
        comport_baud_rate = ComportSetting.objects.values_list('baud_rate', flat=True).first()
        comport_parity = ComportSetting.objects.values_list('parity', flat=True).first()
        comport_stopbit = ComportSetting.objects.values_list('stop_bit', flat=True).first()
        comport_databit = ComportSetting.objects.values_list('data_bit', flat=True).first()


        print('Your baud_rate is this:', comport_baud_rate)
        print('Your COM port is:', comport_com_port)

        com_ports = get_available_com_ports()
        print('Your available COM ports are:', com_ports)

        if com_ports:
            if comport_com_port in com_ports:
                ports_string = comport_com_port
                print('Matching COM port found:', ports_string)
            else:
                ports_string = ', '.join(com_ports)
                print('No matching COM port found. Sending all available ports:', ports_string)
        else:
            ports_string = 'No COM ports available'
            print(ports_string)

        part_model = list(Parameter_Settings.objects.order_by('id').values_list('part_model', flat=True).distinct())
        print('Your part names from database:', part_model)

        user_name = list(User_Data.objects.all().values())
        print('your username is this from databse:',user_name)

        shift_time = list(Data_Shift.objects.all().order_by('id').values())
        print('Your received shift time is this:', shift_time)

        # Fetch all stored values
        new_part = part_retrived.objects.filter(id=1).values('part_name').first()  # Get part_name only

        if new_part:  # Check if data exists
            part_name = new_part['part_name']  # Extract part_name
            print('Part name:', part_name)  # Print only part_name

            # Check if part_name exists in part_model and move it to the first position
            if part_name in part_model:
                part_model.remove(part_name)  # Remove the part_name from its current position
                part_model.insert(0, part_name)  # Insert the part_name at index 0
                print('Updated part_model with part_name at first index:', part_model)
            else:
                print('Part name not found in part_model. No update made.')
        else:
            print('No data found!')  # Handle empty database

        

        username = request.session.get('username', 'Unknown User')

        # Log the username in the console
        print(f'Logged-in User: {username}')

        

        context = {
            'part_model': part_model,
            'comport_com_port': comport_com_port,
            'ports_string': ports_string,
            'comport_baud_rate': comport_baud_rate,
            'comport_parity': comport_parity,
            'comport_stopbit': comport_stopbit,
            'comport_databit': comport_databit,
            'shift_time': json.dumps(shift_time),  # Pass serialized JSON data
            'user_name': json.dumps(user_name),
            'username':username,
        }

        return render(request, 'app/measurement.html', context)
