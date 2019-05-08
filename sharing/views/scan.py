"""
Модули:
    - django:
        - shortcuts
        - contrib.auth.decorators
    - sharing:
        - models
        - views.helpers
"""
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from sharing.models import Profile, Share
from sharing.views.helpers import get_last_order, get_profile, count_profit, \
    end_order, order_duration


@login_required
def scan(request):
    """
    Сканирование кода
    :param request:
    :return:
    """
    profile = get_profile(request.user)
    order = get_last_order(profile)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    if order.progress != 'created' and order.progress != 'applied':
        return redirect('/')
    if request.method == 'POST':
        scanned_code = request.POST.get('qrcode')
        if order.progress == 'created':
            if order.share.qrcode == scanned_code:
                order.progress = 'applied'
                order.save()
                return HttpResponse('session')
        elif order.progress == 'applied':
            shares = Share.objects.all()
            for cand_share in shares:
                if cand_share.qrcode == scanned_code:
                    end_order(order, cand_share)
                    return HttpResponse('end')
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
        # requests.get('http://' + order.share.ip + '/')
        power.status = 'occupied'
    elif power.status == 'returning':
        # requests.get('http://' + order.share.ip + '/')
        power.status = 'charging'
    elif power.status == 'occupied':
        ctx['to_pay'] = count_profit(order)
        ctx['capacity'] = power.capacity
        ctx['timestamp'] = order.timestamp
        ctx['payment_plan'] = order.payment_plan.name
        ctx['wallet'] = order.wallet.name
    power.save()
    return render(request, 'scan/session.html', ctx)


@login_required
def end(request):
    """
    Конец сессии, подсчет денег
    """
    profile = Profile.objects.get(user=request.user)
    order = get_last_order(profile)
    if order.progress != 'ended':
        return redirect('/')
    profit = count_profit(order)
    wal = order.wallet
    wal.balance -= profit
    if wal.balance < 0:
        wal.status = 'suspended'
    wal.save()
    ctx = {
        'to_pay': profit,
        'start': order.share.address,
        'end': order.end_share.address,
        'duration': order_duration(order),
        'wallet': order.wallet.name,
        'payment_plan': order.payment_plan.name,
        'current_balance': wal.balance
    }
    return render(request, 'scan/end.html', ctx)
