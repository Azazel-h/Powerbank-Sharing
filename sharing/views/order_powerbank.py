"""
Модули:
    - django:
        - shortcuts
        - contrib.auth.decorators
    - sharing:
        - models
        - views:
            - scan
            - helpers
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from sharing.models import Share, Powerbank, PaymentPlan, Order
from sharing.views.scan import unverified
from sharing.views.helpers import get_profile, get_last_order, \
     remaining_min, fail_order, has_active_subscription


@login_required
def ordering(request, key):
    """
    Страница заказа
    :param request:
    :param key:
    :return:
    """
    profile = get_profile(request.user)
    share = Share.objects.get(id=key)
    if not profile.active_mail or profile.passport_status != 'success' \
       or not has_active_subscription(profile):
        return unverified(request)
    if get_last_order(profile).progress == 'applied':
        return redirect('/session')
    if get_last_order(profile).progress == 'created':
        return redirect('/pending')
    if share.free_pbs <= 0:
        return redirect('/')
    ctx = {"location": share, "small": False,
           "medium": False, "large": False}
    free_pbs = Powerbank.objects.filter(location=share.id, status='free')
    min_cap = free_pbs[0].capacity
    max_cap = free_pbs[0].capacity
    for powerbank in free_pbs:
        if powerbank.capacity > max_cap:
            max_cap = powerbank.capacity
        if powerbank.capacity < min_cap:
            min_cap = powerbank.capacity
    ctx["key"] = key
    ctx["plans"] = PaymentPlan.objects.all()
    ctx["min_cap"] = min_cap
    ctx["max_cap"] = max_cap
    it_post(request, key, share, ctx)
    return render(request, 'sharing/order.html', context=ctx)


def it_post(request, key, share, ctx):
    """

    :param request:
    :param key:
    :param share:
    :param ctx:
    :return:
    """
    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        pb_capacity = request.POST.get('pb_capacity')
        payment_plan_id = request.POST.get('payment_plan')
        payment_plan = PaymentPlan.objects.filter(id=payment_plan_id)[0]
        if order_type is not None and pb_capacity is not None:
            cands = Powerbank.objects.all().filter(location=key, status='free')
            cand = None
            mx_cand = 0
            for power in cands:
                if power.capacity > mx_cand\
                   and 4001 <= power.capacity <= 10000\
                   and pb_capacity == 'medium':
                    mx_cand = power.capacity
                    cand = power
                if mx_cand < power.capacity <= 4000 and pb_capacity == 'small':
                    mx_cand = power.capacity
                    cand = power
                if power.capacity > mx_cand and pb_capacity == 'large':
                    mx_cand = power.capacity
                    cand = power
            if cand is not None:
                if order_type == 'N':
                    order = Order(payment_plan=payment_plan,
                                  order_type='immediate',
                                  pb=cand,
                                  share=share,
                                  profile=get_profile(request.user),
                                  reservation_time=2,
                                  end_share=share)
                else:
                    order = Order(payment_plan=payment_plan,
                                  order_type='hold',
                                  pb=cand,
                                  share=share,
                                  profile=get_profile(request.user),
                                  end_share=share)
                order.save()
                cand.status = 'ordered'
                # когда юзер отсканит, тогда cand.status = 'occupied'
                share.free_pbs -= 1
                share.save()
                cand.save()
                ctx['order_status'] = 'succeess'
            else:
                ctx['order_status'] = 'fail'
                # не найдено (но такого не будет)


@login_required
def pending(request):
    """
    Страница готовности заказа
    :param request:
    :return:
    """
    profile = get_profile(request.user)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    order = get_last_order(get_profile(request.user))
    rem = remaining_min(order)
    if rem is not None:
        if rem <= 0:
            fail_order(order)
    if order.progress != 'created':
        return redirect('/')
    ctx = {'capacity': str(order.pb.capacity),
           'timestamp': str(order.timestamp),
           'remaining': int(remaining_min(order)),
           'address': order.share.address,
           'plan': order.payment_plan.name}
    return render(request, 'scan/pending.html', context=ctx)


@login_required
def cancelled(request):
    """
    Страница отмененного заказа
    :param request:
    :return:
    """
    orders = Order.objects.filter(profile=get_profile(request.user))
    last = len(orders) - 1
    order = orders[last]
    if order.progress != 'created':
        return redirect('/')
    power = order.pb
    share = order.share
    power.status = 'free'
    power.save()
    order.progress = 'cancelled'
    order.save()
    share.free_pbs += 1
    share.save()
    return render(request, 'scan/cancelled.html')
