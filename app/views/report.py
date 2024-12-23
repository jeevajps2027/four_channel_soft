import json
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
from django.db.models import Q
from collections import defaultdict
from app.models import Data_Shift, MeasurementData, Parameter_Settings, paraTableData


def report(request):
    if request.method == 'POST':
        # Extract the single `data` field from the POST request
        raw_data = request.POST.get('data')
        if raw_data:
            # Parse the JSON string back into a Python dictionary
            data = json.loads(raw_data)
            print("data:", data)

            # Access individual fields from the parsed data
            from_date = data.get('from_date')
            part_model = data.get('part_model')
            mode = data.get('mode')  # 'max', 'min', or 'tir'
            to_date = data.get('to_date')
            shift = data.get('shift')
            status = data.get('status')

            # Validate required fields
            if not all([from_date, to_date, part_model]):
                return JsonResponse({'error': 'Missing required fields: from_date, to_date, or part_model'}, status=400)

            filter_kwargs = {
                'date__range': (from_date, to_date),
                'part_model': part_model,
            }

            if shift != "ALL":
                filter_kwargs['shift'] = shift

            if status != "ALL":
                filter_kwargs['overall_status'] = status

            # Filter the data without converting it to a list
            filtered_data = MeasurementData.objects.filter(**filter_kwargs)

            # # Check if any data exists with comp_sr_no
            # if filtered_data.exclude(comp_sr_no__isnull=True).exclude(comp_sr_no__exact='').exists():
            #     # If data with comp_sr_no exists
            #     distinct_comp_sr_nos = (
            #         filtered_data.exclude(comp_sr_no__isnull=True)
            #         .exclude(comp_sr_no__exact='')
            #         .values_list('comp_sr_no', flat=True)
            #         .distinct()
            #         .order_by('date')
            #     )
            #     print("it contains punch no")
            # else:
            #     # If no data with comp_sr_no exists
            #     distinct_without_comp_sr_nos = (
            #         filtered_data.filter(Q(comp_sr_no__isnull=True) | Q(comp_sr_no__exact=''))
            #         .order_by('date')
            #     )

            #     print("it does not contain punch no")

            #     grouped_by_date = defaultdict(list)
            #     for entry in distinct_without_comp_sr_nos:
            #         grouped_by_date[entry.date].append(entry)

            #     distinct_dates = grouped_by_date.keys()
            #     print("distinct_dates", distinct_dates)
            #     total_count = len(distinct_dates)
            #     print("total_count", total_count)

            #     data_dict = {
            #         'Date': [],
            #         'Operator': [],
            #         'Shift': []
            #     }
            #     parameter_data = paraTableData.objects.filter(
            #         parameter_settings__part_model=part_model
            #     ).values('parameter_name', 'usl', 'lsl')

            #      # Convert to a list if needed
            #     parameter_data_list = list(parameter_data)

            #     # Print the results for debugging
            #     print("Parameter Data:", parameter_data_list)

            #     for param in parameter_data:
            #         param_name = param['parameter_name']
            #         usl = param['usl']
            #         lsl = param['lsl']
            #         key = f"{param_name} <br>{usl} <br>{lsl}"
            #         data_dict[key] = []

            #     data_dict['Status'] = []

                

                # accept_count = 0
                # rework_count = 0
                # reject_count = 0

                # for date, records in grouped_by_date.items():
                #     formatted_date = date.strftime('%d-%m-%Y %I:%M:%S %p')
                #     operator = records[0]['operator']
                #     shift = records[0]['shift']
                   

                #     data_dict['Date'].append(formatted_date)
                #     data_dict['Operator'].append(operator)
                #     data_dict['Shift'].append(shift)

                #     temp_dict = {key: '' for key in data_dict.keys() if key not in ['Date', 'Operator', 'Shift', 'Status']}

                #     for data in records:
                #         parameter_name = data['parameter_name']
                #         print("parameter_name", parameter_name)
                #         usl = paraTableData.objects.get(parameter_name=parameter_name, parameter_settings__part_model=part_model).usl
                #         lsl = paraTableData.objects.get(parameter_name=parameter_name, parameter_settings__part_model=part_model).lsl
                #         print("usl:", usl)
                #         print("lsl:", lsl)
                #         key = f"{parameter_name} <br>{usl} <br>{lsl}"

                #          # Determine which value to display based on `mode`
                #         if mode == 'max':
                #             value_to_display = data['max_value']
                #         elif mode == 'min':
                #             value_to_display = data['min_value']
                #         elif mode == 'tir':
                #             value_to_display = data['tir_value']
                #         else:
                #             value_to_display = data['output']  # Default to `output` if mode is not recognized

                #         # Format the value display with background color based on `overall_status`
                #         if data['overall_status'] == 'ACCEPT':
                #             readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{value_to_display}</span>'
                #         elif data['overall_status'] == 'REWORK':
                #             readings_html = f'<span style="background-color: yellow; padding: 2px;">{value_to_display}</span>'
                #         elif data['overall_status'] == 'REJECT':
                #             readings_html = f'<span style="background-color: red; padding: 2px;">{value_to_display}</span>'

                #         temp_dict[key] = readings_html

                #     for key in temp_dict:
                #         data_dict[key].append(temp_dict[key])

                #     if data['overall_status'] == 'ACCEPT':
                #         status_value = f'<span style="background-color: #00ff00; padding: 2px;">{data['overall_status']}</span>'
                #     elif data['overall_status'] == 'REWORK':
                #         status_value = f'<span style="background-color: yellow; padding: 2px;">{data['overall_status']}</span>'
                #     elif data['overall_status'] == 'REJECT':
                #         status_value = f'<span style="background-color: red; padding: 2px;">{data['overall_status']}</span>'

                    
                #     data_dict['Status'].append(status_value)

                #     df = pd.DataFrame(data_dict)
                # df.index = df.index + 1  # Shift index by 1 to start from 1

                # table_html = df.to_html(index=True, escape=False, classes='table table-striped')
                # print("table_html",table_html)

                            


               


            # Further process the queryset
            distinct_comp_sr_nos = (
                filtered_data.exclude(comp_sr_no__isnull=True)
                .exclude(comp_sr_no__exact='')
                .values_list('comp_sr_no', flat=True)
                .distinct()
                .order_by('date')
            )

            distinct_without_comp_sr_nos = filtered_data.filter(Q(comp_sr_no__isnull=True) | Q(comp_sr_no__exact='')).order_by('date')

            # Convert the queryset to a list if needed for further use
            filtered_data_list = list(filtered_data.values())
            print("Filtered data:", filtered_data_list)
            print("distinct_comp_sr_nos:", list(distinct_comp_sr_nos))

            total_count = distinct_comp_sr_nos.count()
            print(f"Number of distinct comp_sr_no values: {total_count}")

            data_dict = {
                'Date': [],
                'Job Number': [],
                'Shift': [],
                'Operator': [],
            }

            # Fetch all paraTableData entries related to the given part_model
            parameter_data = paraTableData.objects.filter(
                parameter_settings__part_model=part_model
            ).values('parameter_name', 'usl', 'lsl')

            # Convert to a list if needed
            parameter_data_list = list(parameter_data)

            # Print the results for debugging
            print("Parameter Data:", parameter_data_list)

            for param in parameter_data:
                param_name = param['parameter_name']
                usl = param['usl']
                lsl = param['lsl']
                key = f"{param_name} <br>{usl} <br>{lsl}"
                data_dict[key] = []

            data_dict['Status'] = []

            # Create a dictionary to hold rows for each `comp_sr_no`
            rows_dict = {}

            for comp_sr_no in distinct_comp_sr_nos:
                print(f"Processing comp_sr_no: {comp_sr_no}")

                filter_params = filter_kwargs.copy()
                filter_params['comp_sr_no'] = comp_sr_no

                part_status = MeasurementData.objects.filter(**filter_params).values_list('overall_status', flat=True).distinct().first()
                print(f"Part Status: {part_status}")

                comp_sr_no_data = MeasurementData.objects.filter(**filter_params).values(
                    'parameter_name', 'output', 'operator', 'shift', 'date', 'overall_status', 'max_value', 'min_value', 'tir_value'
                ).order_by('date')
                print("comp_sr_no_data", comp_sr_no_data)

                # Create an empty row for the comp_sr_no if it doesn't exist
                if comp_sr_no not in rows_dict:
                    rows_dict[comp_sr_no] = {
                        'Date': '',
                        'Job Number': comp_sr_no,
                        'Shift': '',
                        'Operator': '',
                        'Status': '',
                    }

                combined_row = rows_dict[comp_sr_no]

                for data in comp_sr_no_data:
                    parameter_name = data['parameter_name']
                    print("parameter_name", parameter_name)
                    usl = paraTableData.objects.get(parameter_name=parameter_name, parameter_settings__part_model=part_model).usl
                    lsl = paraTableData.objects.get(parameter_name=parameter_name, parameter_settings__part_model=part_model).lsl
                    print("usl:", usl)
                    print("lsl:", lsl)
                    key = f"{parameter_name} <br>{usl} <br>{lsl}"
                    formatted_date = data['date'].strftime('%d-%m-%Y %I:%M:%S %p')
                    print("formatted_date", formatted_date)

                    # Determine which value to display based on `mode`
                    if mode == 'max':
                        value_to_display = data['max_value']
                    elif mode == 'min':
                        value_to_display = data['min_value']
                    elif mode == 'tir':
                        value_to_display = data['tir_value']
                    else:
                        value_to_display = data['output']  # Default to `output` if mode is not recognized

                    # Format the value display with background color based on `overall_status`
                    if data['overall_status'] == 'ACCEPT':
                        readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{value_to_display}</span>'
                    elif data['overall_status'] == 'REWORK':
                        readings_html = f'<span style="background-color: yellow; padding: 2px;">{value_to_display}</span>'
                    elif data['overall_status'] == 'REJECT':
                        readings_html = f'<span style="background-color: red; padding: 2px;">{value_to_display}</span>'

                    # Append the value to the corresponding parameter column
                    combined_row[key] = combined_row.get(key, '') + f' {readings_html}'
                    combined_row['Date'] = formatted_date
                    combined_row['Operator'] = data['operator']
                    combined_row['Shift'] = data['shift']

                    if data['overall_status'] == 'ACCEPT':
                        status_value = f'<span style="background-color: #00ff00; padding: 2px;">{data['overall_status']}</span>'
                    elif data['overall_status'] == 'REWORK':
                        status_value = f'<span style="background-color: yellow; padding: 2px;">{data['overall_status']}</span>'
                    elif data['overall_status'] == 'REJECT':
                        status_value = f'<span style="background-color: red; padding: 2px;">{data['overall_status']}</span>'

                    combined_row['Status'] = status_value

            # Now prepare the final data for rendering the table
            for key in data_dict:
                data_dict[key] = []

            for row in rows_dict.values():
                for key, value in row.items():
                    data_dict[key].append(value)

            df = pd.DataFrame(data_dict)
            df.index = df.index + 1

            table_html = df.to_html(index=True, escape=False, classes='table table-striped')

            print("table_html", table_html)
            return JsonResponse({
                'table_html': table_html,
                'total_count':total_count,
                })


                                                
                
           
    
    elif request.method == 'GET':
        shift_values = Data_Shift.objects.order_by('id').values_list('shift', 'shift_time').distinct()
        shift_name_queryset = Data_Shift.objects.order_by('id').values_list('shift', flat=True).distinct()
        shift_name = list(shift_name_queryset)
        print ("shift_name",shift_name)

        # Convert the QuerySet to a list of lists
        shift_values_list = list(shift_values)
        
        # Serialize the list to JSON
        shift_values_json = json.dumps(shift_values_list)
        print("shift_values_json",shift_values_json)

         # Create a context dictionary to pass the data to the template
        context = {
            'shift_values': shift_values_json,
            'shift_name':shift_name,
        }
    return render(request,'app/report.html',context)