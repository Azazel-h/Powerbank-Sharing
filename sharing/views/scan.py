from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sharing.models import Profile
import requests
from sharing.views.helpers import get_last_order, get_profile, count_profit


@login_required
def scan(request):
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
                return render(request, 'scan/session.html')
        else:
            '''
                energo Pro - мнговенный заказ пб без бронирования
            '''
            pass
    else:
        return render(request, 'scan/scan.html')


def unverified(request):
    profile = Profile.objects.get(user=request.user)
    reasons = []
    if not profile.active_mail:
        reasons.append('Не активирован почтовый адрес')
    if not profile.passport_status == 'success':
        reasons.append('Не подтверждён паспорт')
    return render(request, 'scan/unverified.html', {'reasons': reasons})


@login_required
def session(request):
    profile = Profile.objects.get(user=request.user)
    order = get_last_order(profile)
    pb = order.pb
    ctx = {}
    if not order.progress == 'applied':
        return redirect('/')
    """
        Обработка начала/конца сессии -- выдача пб, валидация сессии, прочее
    """
    if pb.status == 'ordered':
        ejreq = requests.get('http://' + order.share.ip + '/')
        # Начать оплату
        pb.status = 'occupied'
    elif pb.status == 'returning':
        ejreq = requests.get('http://' + order.share.ip + '/')
        # Конец оплаты
        pb.status = 'charging'
    elif pb.status == 'occupied':
        ctx['to_pay'] = count_profit(order)
        ctx['capacity'] = pb.capacity
        ctx['timestamp'] = order.timestamp
        ctx['payment_plan'] = order.payment_plan.name
        ctx['wallet'] = order.wallet.name
    pb.save()
    # Текущая оплата...
    return render(request, 'scan/session.html', ctx)
