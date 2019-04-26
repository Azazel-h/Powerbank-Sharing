from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from sharing.models import PaymentPlan, Wallet
from sharing.views.helpers import get_profile


@login_required
def add_payment_plan(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        payment_type = request.POST.get('payment_type')
        cost = request.POST.get('cost')
        payment_plan = PaymentPlan(name=name, description=description, payment_type=payment_type, cost=cost)
        payment_plan.save()
        return HttpResponse('Новый тариф успешно добавлен!')
    return render(request, 'payment/add_payment_plan.html')


@login_required
def add_wallet(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        payment_method = request.POST.get('payment_method')
        balance = request.POST.get('balance')
        wallet = Wallet(name=name, payment_method=payment_method, status='active', balance=balance)
        profile = get_profile(request.user)
        wallet.save()
        wallet_str = profile.wallets
        new_wallet_str = wallet_str + str(wallet.id) + ' '
        profile.wallets = new_wallet_str
        profile.save()
        return HttpResponse('Новый кошелёк успешно добавлен!')
    return render(request, 'payment/add_wallet.html')