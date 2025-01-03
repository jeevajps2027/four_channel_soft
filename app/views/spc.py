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
            part_model = data.get('partModel')
            # parameter_name = "ALL"
            parameter_name = data.get('parameterName')

            if not part_model or not parameter_name:
                return JsonResponse({'error': 'Missing partModel or parameterName.'}, status=400)

            # Handle multiple parameters if "ALL" is specified
            parameter_names = [parameter_name] if parameter_name != "ALL" else list(
                paraTableData.objects.filter(
                    parameter_settings__part_model=part_model
                ).values_list('parameter_name', flat=True)
            )

            charts_html = []

            for pname in parameter_names:
                # Query readings and metadata for the current parameter
                readings = list(
                    MeasurementData.objects.filter(
                        part_model=part_model, parameter_name=pname
                    ).order_by('-date')[:25].values_list('output', flat=True)
                )[::-1]

                dates = list(
                    MeasurementData.objects.filter(
                        part_model=part_model, parameter_name=pname
                    ).order_by('-date')[:25].values_list('date', flat=True)
                )[::-1]

                limits = MeasurementData.objects.filter(
                    part_model=part_model, parameter_name=pname
                ).order_by('date').values('usl', 'lsl', 'utl', 'ltl', 'nominal').first()

                if not readings or not limits:
                    charts_html.append(f"<div>No data available for parameter: {pname}</div>")
                    continue

                readings = [float(r) for r in readings]
                x_bar = np.mean(readings)
                usl, lsl, utl, ltl, nominal = (
                    limits['usl'], limits['lsl'], limits['utl'], limits['ltl'], limits['nominal']
                )

                # Define traces for the graph
                traces = [
                    go.Scatter(
                        x=list(range(len(readings))), y=readings, mode='lines+markers', name='Readings',
                        marker=dict(color='black')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[x_bar] * len(readings), mode='lines',
                        name=f'X-bar ({x_bar:.5f})', line=dict(color='purple')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[nominal] * len(readings), mode='lines',
                        name=f'Nominal ({nominal})', line=dict(color='green')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[usl] * len(readings), mode='lines',
                        name=f'USL ({usl})', line=dict(color='red', dash='dash')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[lsl] * len(readings), mode='lines',
                        name=f'LSL ({lsl})', line=dict(color='red', dash='dash')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[utl] * len(readings), mode='lines',
                        name=f'UTL ({utl})', line=dict(color='purple', dash='dot')
                    ),
                    go.Scatter(
                        x=list(range(len(readings))), y=[ltl] * len(readings), mode='lines',
                        name=f'LTL ({ltl})', line=dict(color='orange', dash='dot')
                    ),
                ]

                # Define background color regions
                shapes = [
                    dict(type='rect', x0=0, x1=len(readings) - 1, y0=lsl, y1=usl, fillcolor='rgba(0,255,0,0.2)', line=dict(width=0)),
                    dict(type='rect', x0=0, x1=len(readings) - 1, y0=usl, y1=utl, fillcolor='rgba(255,255,0,0.2)', line=dict(width=0)),
                    dict(type='rect', x0=0, x1=len(readings) - 1, y0=ltl, y1=lsl, fillcolor='rgba(255,255,0,0.2)', line=dict(width=0)),
                    dict(type='rect', x0=0, x1=len(readings) - 1, y0=min(ltl, min(readings)) - 0.02, y1=ltl, fillcolor='rgba(255,0,0,0.2)', line=dict(width=0)),
                    dict(type='rect', x0=0, x1=len(readings) - 1, y0=utl, y1=max(utl, max(readings)) + 0.02, fillcolor='rgba(255,0,0,0.2)', line=dict(width=0)),
                ]

                # Create figure layout
                layout = go.Layout(
                    title=f'X-bar Control Chart for {pname}',
                    xaxis=dict(title='Sample Number'),
                    yaxis=dict(title='Measurement'),
                    shapes=shapes,
                    hovermode='closest'
                )

                fig = go.Figure(data=traces, layout=layout)
                charts_html.append(plot(fig, output_type='div'))

            # If we have multiple graphs, send them separately as individual responses
            if len(charts_html) > 1:
                return JsonResponse({
                    'chart_html': charts_html,
                    'message': 'Multiple charts generated successfully!'
                })
            else:
                # If there's only one graph, send it as a single response
                return JsonResponse({
                    'chart_html': charts_html[0],
                    'message': 'Chart generated successfully!'
                })

        except Exception as e:
            print("Error:", str(e))
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