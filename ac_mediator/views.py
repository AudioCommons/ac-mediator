import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/')
def crash_me(request):
    raise Exception('Everything is under control')


@login_required
def monitor(request):
    flower_auth = os.getenv('FLOWER_BASIC_AUTH', ':').split(':')
    redmon_auth = os.getenv('FLOWER_BASIC_AUTH', ':').split(':')
    return render(request, 'admin/monitor.html', {
        'flower_auth': flower_auth,
        'redmon_auth': redmon_auth,
    })
