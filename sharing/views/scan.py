"""
Модули:
    - django:
        - shortcuts
        - contrib.auth.decorators
    - sharing:
        - models
        - views.helpers
"""
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sharing.models import Profile
from sharing.views.helpers import get_last_order, get_profile, count_profit


@login_required
def scan(request):
    """
    Сканирование и переход на страницу сессии
    :param request:
    :return:
    """
    profile = get_profile(request.user)
    order = get_last_order(profile)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    if order.progress != 'created':
        return redirect('/')
    if request.method == 'POST':
        scanned_code = request.POST.get('qrcode')
        if order.progress == 'created':
            if order.share.qrcode == scanned_code:
                order.progress = 'applied'
                order.save()
                page = 'scan/session.html'
    else:
        page = 'scan/scan.html'
    return render(request, page)


def unverified(request):
    """
    Страница причины отказа
    :param request:
    :return:
    """
    profile = Profile.objects.get(user=request.user)
    reasons = []
    if not profile.active_mail:
        reasons.append('Не активирован почтовый адрес')
    if not profile.passport_status == 'success':
        reasons.append('Не подтверждён паспорт')
    return render(request, 'scan/unverified.html', {'reasons': reasons})


@login_required
def session(request):
    """
    Страница сессиии
    :param request:
    :return:
    """
    profile = Profile.objects.get(user=request.user)
    order = get_last_order(profile)
    power = order.pb
    ctx = {}
    if order.progress != 'applied':
        return redirect('/')
    if power.status == 'ordered':
        requests.get('http://' + order.share.ip + '/')
        power.status = 'occupied'
    elif power.status == 'returning':
        requests.get('http://' + order.share.ip + '/')
        power.status = 'charging'
    elif power.status == 'occupied':
        ctx['to_pay'] = count_profit(order)
        ctx['capacity'] = power.capacity
        ctx['timestamp'] = order.timestamp
        ctx['payment_plan'] = order.payment_plan.name
        ctx['wallet'] = order.wallet.name
    power.save()
    return render(request, 'scan/session.html', ctx)
