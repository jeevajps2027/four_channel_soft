import json
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from app.models import Parameter_Settings,paraTableData,master_data
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


@csrf_exempt
def master(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.POST.get('payload', '[]'))  # Parse the JSON payload
        print('your data from front end:',data)
        for item in data:
            try:
                # Validate and parse date_time
                date_time = datetime.strptime(item['date_time'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS.'}, status=400)

            # Save data to MasterData
            master_data.objects.create(
                a=item['a'],
                a1=item['a1'],
                b=item['b'],
                b1=item['b1'],
                e=item['e'],
                d=item['d'],
                o1=item['o1'],
                parameter_name=item['parameter_name'],
                part_model=item['part_model'],
                date_time=date_time,
                mastering=item['mastering'],
                probe_number = item['probeNumber']
            )

            

        # Handle AJAX POST
        part_name = request.POST.get('part_name', '')
        print(f"your received value from front end:: {part_name}")

        # Filter all Parameter_Settings entries matching the part_model
        matching_settings = Parameter_Settings.objects.filter(part_model=part_name)
        parameter_names = []
        low_masters = []
        high_masters = []
        probe_number = []
        nominals = []
        lsls = []
        usls = []
        ltls = []
        utls = []
        stepnumbers = []
        idorod = []

        if matching_settings.exists():
            print(f"Matching Parameter_Settings entries for part_model '{part_name}':")
            for setting in matching_settings:
                print(f"Parameter_Settings ID: {setting.id}, sr_no: {setting.sr_no}, part_name: {setting.part_name}")
                
                # Filter related paraTableData entries for each setting
                related_data = paraTableData.objects.filter(parameter_settings=setting).order_by('id')
                
                
                if related_data.exists():
                    print(f"Related paraTableData entries for Parameter_Settings ID {setting.id}:")
                    for data in related_data:

                        print(
                            f"  Parameter Name: {data.parameter_name}, "
                            f"Channel No: {data.channel_no}, "
                            f"Nominal: {data.nominal}, "
                            f"LSL: {data.lsl}, "
                            f"USL: {data.usl}, "
                            f"Digits: {data.digits}, "
                            f"low_master:{data.low_master}, "
                            f"high_master:{data.high_master}, "
                            f"ltl:{data.ltl}, "
                            f"utl:{data.utl}, "
                            f"step_no:{data.step_no}, "
                            f"id_od:{data.id_od}, "
                        )

                        parameter_names.append(data.parameter_name)  # Collect parameter names
                        low_masters.append(data.low_master)
                        high_masters.append(data.high_master)
                        probe_number.append(data.channel_no)
                        nominals.append(data.nominal)
                        lsls.append(data.lsl)
                        usls.append(data.usl)
                        ltls.append(data.ltl)
                        utls.append(data.utl)
                        stepnumbers.append(data.step_no)
                        idorod.append(data.id_od)


                else:
                    print(f"  No paraTableData entries found for Parameter_Settings ID {setting.id}")
        else:
            print(f"No Parameter_Settings entries found for part_model '{part_name}'")

        # Respond with redirect URL for client-side navigation
        return JsonResponse({
            "redirect_url": reverse('master'),
            "parameter_names": parameter_names, 
            "low_masters":low_masters, 
            "high_masters":high_masters,
            "probe_number":probe_number,
            "nominals":nominals,
            "lsls":lsls,
            "usls":usls,
            "ltls":ltls,
            "utls":utls,
            "stepnumbers":stepnumbers,
            "idorod":idorod,
        })

    # Render the page with the part_name (default to empty string if not provided)
    part_name = request.GET.get('part_model', '')  # Optional: Use a query param or other logic
    return render(request, 'app/master.html', {'part_name': part_name})