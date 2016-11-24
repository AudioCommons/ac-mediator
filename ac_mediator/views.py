import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def monitor(request):
    flower_auth = os.getenv('FLOWER_BASIC_AUTH', ':').split(':')
    redmon_auth = os.getenv('FLOWER_BASIC_AUTH', ':').split(':')
    return render(request, 'admin/monitor.html', {
        'flower_auth': flower_auth,
        'redmon_auth': redmon_auth,
    })
