from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from sharing.models import Share, Powerbank
import json
from random import random


@login_required
def add_powerbank_sharing(request):
    if request.user.is_superuser is False:
        return redirect('/')

    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        qrcode = request.POST.get('qrcode')
        ip = request.POST.get('ip')
        crds = json.loads(request.POST.get('crds'))
        new_sharing = Share(title=title, address=address, crds_lot=crds[0], crds_lat=crds[1], qrcode=qrcode, ip=ip)
        new_sharing.save()
        return HttpResponse('Новая точка выдачи успешно добавлена!')
    context = {}
    return render(request, 'sharing/add.html', context)


@login_required
def add_pb(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        code = random()
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')
        new_pb = Powerbank(code=code, location=location, capacity=capacity, status='free')
        share = Share.objects.get(id=location)
        share.free_pbs += 1
        share.save()
        new_pb.save()
        return HttpResponse('Новый powerbank успешно добавлен!')
    return render(request, 'sharing/add_pb.html')


@login_required
def share_page(request, pk):
    pbs = Powerbank.objects.filter(location=pk, status='free')
    pb_size = len(pbs)
    if pb_size == 0:
        min_cap = max_cap = 0
    elif pb_size == 1:
        min_cap = max_cap = pbs[0].capacity
    else:
        min_cap = pbs[0].capacity
        max_cap = pbs[1].capacity
        for pb in pbs:
            if pb.capacity > max_cap:
                max_cap = pb.capacity
            if pb.capacity < min_cap:
                min_cap = pb.capacity
    context = {
        'share': Share.objects.get(id=pk),
        'min_cap': min_cap,
        'max_cap': max_cap,
        'amt': pb_size
    }
    return render(request, 'sharing/share_page.html', context)