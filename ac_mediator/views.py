from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def monitor(request):
    return render(request, 'admin/monitor.html', {})


@login_required
def get_monitor_status(request):
    return JsonResponse({'test': 123})
