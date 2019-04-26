from django.contrib.auth.decorators import login_required
from sharing.models import Share, Powerbank, Wallet, PaymentPlan, Order
from django.shortcuts import render, redirect
from sharing.views.scan import unverified
from sharing.views.helpers import get_profile, get_last_order, \
     remaining_min, fail_order


@login_required
def ordering(request, pk):
    profile = get_profile(request.user)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    if get_last_order(profile).progress == 'applied':
        return redirect('/session')
    share = Share.objects.get(id=pk)
    ctx = {"location": share.address}
    ctx["small"] = False
    ctx["medium"] = False
    ctx["large"] = False
    for pb in Powerbank.objects.filter(location=share.id, status='free'):
        if pb.capacity <= 4000:
            ctx["small"] = True
        if 4001 <= pb.capacity <= 10000:
            ctx["medium"] = True
        if pb.capacity >= 10001:
            ctx["large"] = True
    ctx["pk"] = pk
    wallets_id = list(map(int, profile.wallets.split()))
    wallets = []
    for wid in wallets_id:
        wallets.append(Wallet.objects.filter(id=wid)[0])
    ctx["plans"] = PaymentPlan.objects.all()
    ctx["wallets"] = wallets

    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        pb_capacity = request.POST.get('pb_capacity')
        payment_plan_id = request.POST.get('payment_plan')
        wallet_id = request.POST.get('wallet')
        payment_plan = PaymentPlan.objects.filter(id=payment_plan_id)[0]
        wallet = Wallet.objects.filter(id=wallet_id)[0]
        if order_type is not None and pb_capacity is not None:
            cands = Powerbank.objects.all().filter(location=pk, status='free')
            cand = None
            if pb_capacity == 'small':
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand and pb.capacity <= 4000:
                        mx_cand = pb.capacity
                        cand = pb
            elif pb_capacity == 'medium':
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand and 4001 <= pb.capacity <= 10000:
                        mx_cand = pb.capacity
                        cand = pb
            elif pb_capacity == 'large':
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand:
                        mx_cand = pb.capacity
                        cand = pb
            else:
                pass
            if cand is not None:
                if order_type == 'N':
                    order = Order(wallet=wallet,
                                  payment_plan=payment_plan,
                                  order_type='immediate',
                                  pb=cand,
                                  share=share,
                                  profile=get_profile(request.user),
                                  reservation_time=2)
                else:
                    order = Order(wallet=wallet,
                                  payment_plan=payment_plan,
                                  order_type='hold',
                                  pb=cand,
                                  share=share,
                                  profile=get_profile(request.user))
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
    return render(request, 'sharing/order.html', context=ctx)


@login_required
def pending(request):
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
    ctx = {}
    ctx['capacity'] = str(order.pb.capacity)
    ctx['timestamp'] = str(order.timestamp)
    ctx['remaining'] = int(remaining_min(order))
    ctx['address'] = order.share.address
    ctx['plan'] = order.payment_plan.name
    ctx['wallet'] = order.wallet.name
    return render(request, 'scan/pending.html', context=ctx)


@login_required
def cancelled(request):
    orders = Order.objects.filter(profile=get_profile(request.user))
    last = len(orders) - 1
    order = orders[last]
    if order.progress != 'created':
        return redirect('/')
    pb = order.pb
    share = order.share
    pb.status = 'free'
    pb.save()
    order.progress = 'cancelled'
    order.save()
    share.free_pbs += 1
    share.save()
    return render(request, 'scan/cancelled.html')
