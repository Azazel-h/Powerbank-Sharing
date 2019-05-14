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
from sharing.models import PaymentPlan
from sharing.views.helpers import get_profile


@login_required
def add_payment_plan(request):
    """
    Страница добавления подписки
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        duration = request.POST.get('duration')
        payment_plan = PaymentPlan(name=name,
                                   description=description,
                                   cost=cost,
                                   duration=duration)
        payment_plan.save()
        return HttpResponse('Новая подписка успешно добавлена!')
    return render(request, 'payment/add_payment_plan.html')


@login_required
def subscribe(request):
    """
    Страница оформления подписки
    :param request:
    :return:
    """
    profile = get_profile(request.user)
    if request.method == 'POST':
        payment_plan_id = int(request.POST.get('payment_plan_id'))
        payment_plan = PaymentPlan.objects.filter(id=payment_plan_id)
        if payment_plan is not None:
            profile.payment_plan = payment_plan
            profile.save()
        return HttpResponse('Подписка привязана')
    return render(request, 'payment/subscribe.html')
