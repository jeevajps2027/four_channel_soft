import json
from django.shortcuts import render

from app.models import Parameter_Settings, paraTableData,MeasurementData
import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt  # Remove in production; use CSRF token instead
def spc(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            print("Parsed data:", data)

            part_model = data.get('partModel')
            parameter_name = data.get('parameterName')

            if not part_model or not parameter_name:
                return JsonResponse({'error': 'Missing partModel or parameterName.'}, status=400)

            # # Query for the last 25 readings ordered by date
            # filtered_readings = MeasurementData.objects.filter(
            #     part_model=part_model, parameter_name=parameter_name
            # ).order_by('date')[:25].values_list('output', flat=True)

            #  # Query for the last 25 readings ordered by date
            # filtered_date_time = MeasurementData.objects.filter(
            #     part_model=part_model, parameter_name=parameter_name
            # ).order_by('date')[:25].values_list('date', flat=True)

            # print("filtered_date_time",filtered_date_time)

            # Query for the last 25 readings ordered by date (newest to oldest)
            filtered_readings = MeasurementData.objects.filter(
                part_model=part_model, parameter_name=parameter_name
            ).order_by('-date')[:25].values_list('output', flat=True)

            # Query for the corresponding dates for the last 25 readings ordered by date
            filtered_date_time = MeasurementData.objects.filter(
                part_model=part_model, parameter_name=parameter_name
            ).order_by('-date')[:25].values_list('date', flat=True)

            # If you want the results in ascending order (oldest to newest)
            filtered_readings = list(reversed(filtered_readings))
            filtered_date_time = list(reversed(filtered_date_time))

            print("filtered_date_time", filtered_date_time)


            

            # Check if readings are available
            if not filtered_readings:
                return JsonResponse({'error': 'No readings found for the given parameters.'}, status=404)

            total_count = len(filtered_readings)
            print("filtered_readings:", filtered_readings)
            print("total_count:", total_count)

            # Convert readings to floats
            readings = [float(r) for r in filtered_readings]

            # Query for the latest values of usl, lsl, nominal, ltl, utl
            filtered_data = MeasurementData.objects.filter(
                part_model=part_model, parameter_name=parameter_name
            ).order_by('date').values('usl', 'lsl', 'utl', 'ltl', 'nominal').first()

            if filtered_data:
                usl = filtered_data.get('usl')
                lsl = filtered_data.get('lsl')
                nominal = filtered_data.get('nominal')
                ltl = filtered_data.get('ltl')
                utl = filtered_data.get('utl')
            else:
                return JsonResponse({'error': 'No matching records found for usl, lsl, nominal, etc.'}, status=404)

            if readings and usl and lsl and nominal and ltl and utl:
                x_bar = np.mean(readings)

                  # Adjust the y-axis range
                y_min = min(ltl, min(readings)) - 0.02  # Extend slightly below LTL
                y_max = max(utl, max(readings)) + 0.02  # Extend slightly above UTL


                # Define traces for the limits and nominal
                trace_nominal = go.Scatter(
                    x=list(range(len(readings))),
                    y=[nominal] * len(readings),
                    mode='lines',
                    name=f'Nominal ({nominal})',
                    line=dict(color='green', dash='solid')
                )
                trace_usl = go.Scatter(
                    x=list(range(len(readings))),
                    y=[usl] * len(readings),
                    mode='lines',
                    name=f'USL ({usl})',
                    line=dict(color='red', dash='dash')
                )
                trace_lsl = go.Scatter(
                    x=list(range(len(readings))),
                    y=[lsl] * len(readings),
                    mode='lines',
                    name=f'LSL ({lsl})',
                    line=dict(color='red', dash='dash')
                )
                trace_ltl = go.Scatter(
                    x=list(range(len(readings))),
                    y=[ltl] * len(readings),
                    mode='lines',
                    name=f'LTL ({ltl})',
                    line=dict(color='orange', dash='dot')
                )
                trace_utl = go.Scatter(
                    x=list(range(len(readings))),
                    y=[utl] * len(readings),
                    mode='lines',
                    name=f'UTL ({utl})',
                    line=dict(color='purple', dash='dot')
                )

                # Define trace for the readings
                trace_readings = go.Scatter(
                    x=list(range(len(readings))),
                    y=readings,
                    mode='lines+markers',
                    name='Readings',
                    marker=dict(color='black')
                )

                # Define trace for the X-bar line
                trace_xbar = go.Scatter(
                    x=list(range(len(readings))),
                    y=[x_bar] * len(readings),
                    mode='lines',
                    name=f'X-bar (Mean: {x_bar:.5f})',
                    line=dict(color='purple', dash='solid')
                )

                # Create shaded areas for different regions
                shapes = [
                    # Green background between LSL and USL
                    dict(
                        type='rect',
                        x0=0,
                        x1=len(readings) - 1,
                        y0=lsl,
                        y1=usl,
                        fillcolor='rgba(0,255,0,0.5)',  # Green with transparency
                        line=dict(width=0),
                    ),
                    # Yellow background between USL and UTL
                    dict(
                        type='rect',
                        x0=0,
                        x1=len(readings) - 1,
                        y0=usl,
                        y1=utl,
                        fillcolor='rgba(255,255,0,0.5)',  # Yellow with transparency
                        line=dict(width=0),
                    ),
                    # Yellow background between LSL and LTL
                    dict(
                        type='rect',
                        x0=0,
                        x1=len(readings) - 1,
                        y0=ltl,
                        y1=lsl,
                        fillcolor='rgba(255,255,0,0.5)',  # Yellow with transparency
                        line=dict(width=0),
                    ),
                    # Red background outside the ranges (less than LTL or greater than UTL)
                    dict(
                        type='rect',
                        x0=0,
                        x1=len(readings) - 1,
                        y0=y_min,
                        y1=ltl,
                        fillcolor='rgba(255,0,0,0.5)',  # Red with transparency
                        line=dict(width=0),
                    ),
                    dict(
                        type='rect',
                        x0=0,
                        x1=len(readings) - 1,
                        y0=utl,
                        y1=y_max,
                        fillcolor='rgba(255,0,0,0.5)',  # Red with transparency
                        line=dict(width=0),
                    ),
                ]

                # Compile all traces
                data = [trace_nominal, trace_usl, trace_lsl, trace_ltl, trace_utl, trace_readings]

                # Define layout with expanded y-axis range
                layout = go.Layout(
                    title='X-bar Control Chart',
                    xaxis_title='Sample Number',
                    yaxis=dict(
                        title='Measurement',
                        range=[y_min, y_max]  # Ensure all lines and readings are visible
                    ),
                    hovermode='closest',
                    width=1500,  # Set the chart width to 1500px
                    shapes=shapes,  # Add shapes (background color)
                )

                # Create figure and convert to HTML
                fig = go.Figure(data=data, layout=layout)
                chart_html = plot(fig, output_type='div')

                # Prepare table content
            table_html = '<table border="1" style="width:100%; text-align:center;">'
            table_html += '<tr><th>NO</th>'  # Heading row for NO
            for i in range(1, 26):
                table_html += f'<th>{i}</th>'
            table_html += '</tr>'

            # Date row
            table_html += '<tr><td>Date</td>'
            for dt in filtered_date_time:
                table_html += f'<td>{dt.strftime("%Y-%m-%d")}</td>'
            table_html += '</tr>'

            # Time row
            table_html += '<tr><td>Time</td>'
            for dt in filtered_date_time:
                table_html += f'<td>{dt.strftime("%H:%M:%S")}</td>'
            table_html += '</tr>'

            # Readings row
            table_html += '<tr><td>Readings</td>'
            for reading in filtered_readings:
                table_html += f'<td>{reading}</td>'
            table_html += '</tr>'

            table_html += '</table>'

            return JsonResponse({
                'table_html': table_html,
                'chart_html': chart_html,
                'usl':usl,
                'lsl':lsl,
                'utl':utl,
                'ltl':ltl,
                'nominal':nominal,
                'mean':x_bar,
                })

                


        except Exception as e:
            # Log the exception for debugging
            print("Unexpected error:", str(e))
            return JsonResponse({'error': 'An unexpected error occurred.', 'details': str(e)}, status=500)

          
    elif request.method == 'GET':
        part_model = request.GET.get('part_model', '')
        # Process the part_model as needed
        print(f'Received part model: {part_model}')

        parameter_setting = Parameter_Settings.objects.get(part_model=part_model)
            # Get all related paraTableData
        parameter_names = list(paraTableData.objects.filter(parameter_settings=parameter_setting).values_list('parameter_name', flat=True))
        print("parameter_names",parameter_names)

        context ={
            'parameter_names':parameter_names,
        }
        
    return render(request,'app/spc.html',context)